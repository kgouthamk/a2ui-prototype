"""The agent seam.

THE RULE: the web layer only calls `enrich()`. It never imports litellm or knows
the model. To migrate to Google ADK later, rewrite ONLY this file — the schema,
prompt, API, and frontend are untouched.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import litellm
from dotenv import load_dotenv
from pydantic import ValidationError

from app.agent.prompt import build_messages
from app.schema.a2ui import A2UINode, EnrichResult, WidgetType

logger = logging.getLogger(__name__)

# litellm calls load_dotenv() when imported, but only finds a .env relative to the
# process CWD — so the key silently vanishes if uvicorn is started from the repo
# root instead of backend/. Pin it to backend/.env. Existing env vars win.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Default: Google Gemini (AI Studio free tier). Needs GEMINI_API_KEY (starts "AIza").
MODEL = os.getenv("A2UI_MODEL", "gemini/gemini-2.0-flash")
# Only used by local providers (e.g. ollama); harmless otherwise.
API_BASE = os.getenv("A2UI_API_BASE", "http://localhost:11434")


def _fallback(markdown: str, reason: str) -> EnrichResult:
    """Never crash the UI: if the model misbehaves, show the markdown plainly.

    The fallback echoes the input verbatim inside Card > MarkdownBlock. That shape
    is easy to mistake for a real-but-unambitious model response, so every fallback
    is logged with WHY — an auth or quota failure must never look like widget choice.
    """
    logger.warning("enrich: returning plain-markdown fallback (reason=%s)", reason)
    return EnrichResult(
        markdown=markdown,
        a2ui=A2UINode(
            type=WidgetType.CARD,
            children=[A2UINode(type=WidgetType.MARKDOWN, props={"markdown": markdown})],
        ),
    )


def enrich(markdown: str) -> EnrichResult:
    """Transform arbitrary markdown into {cleaned markdown, A2UI tree}.

    Set A2UI_STRICT=1 to re-raise instead of falling back — use it in evals, so a
    broken key fails the run loudly rather than scoring the fallback as a result.
    """
    # Offline demo: run the full app with no API key (A2UI_DEMO=1).
    if os.getenv("A2UI_DEMO"):
        from app.agent.demo import DEMO
        return DEMO

    strict = bool(os.getenv("A2UI_STRICT"))

    kwargs = {
        "model": MODEL,
        "messages": build_messages(markdown),
        "response_format": {"type": "json_object"},
        "temperature": float(os.getenv("A2UI_TEMPERATURE", "0")),
    }
    # Ollama (and other local providers) need an explicit api_base.
    if MODEL.startswith("ollama"):
        kwargs["api_base"] = API_BASE

    # Each stage fails differently and is worth telling apart: a dead key, a model
    # that ignored json_object, and a model that emitted an off-catalog widget are
    # three separate bugs with three separate fixes.
    try:
        resp = litellm.completion(**kwargs)
    except Exception as exc:
        logger.error("enrich: call to %s failed — %s: %s", MODEL, type(exc).__name__, exc)
        if strict:
            raise
        return _fallback(markdown, f"model_call_failed:{type(exc).__name__}")

    try:
        raw = resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        logger.error("enrich: unexpected response shape from %s — %s", MODEL, exc)
        if strict:
            raise
        return _fallback(markdown, "malformed_response")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("enrich: %s returned non-JSON (%s); first 300 chars: %r",
                     MODEL, exc, (raw or "")[:300])
        if strict:
            raise
        return _fallback(markdown, "invalid_json")

    try:
        return EnrichResult.model_validate(data)  # catalog + shape enforced here
    except ValidationError as exc:
        logger.error("enrich: %s returned JSON that violates the A2UI contract — %s",
                     MODEL, exc)
        if strict:
            raise
        return _fallback(markdown, "schema_violation")
