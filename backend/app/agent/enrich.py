"""The agent seam.

THE RULE: the web layer only calls `enrich()`. It never imports litellm or knows
the model. To migrate to Google ADK later, rewrite ONLY this file — the schema,
prompt, API, and frontend are untouched.
"""
from __future__ import annotations

import json
import os

import litellm
from pydantic import ValidationError

from app.agent.prompt import build_messages
from app.schema.a2ui import A2UINode, EnrichResult, WidgetType

# Default: Google Gemini (AI Studio free tier). Needs GEMINI_API_KEY (starts "AIza").
MODEL = os.getenv("A2UI_MODEL", "gemini/gemini-2.0-flash")
# Only used by local providers (e.g. ollama); harmless otherwise.
API_BASE = os.getenv("A2UI_API_BASE", "http://localhost:11434")


def _fallback(markdown: str) -> EnrichResult:
    """Never crash the UI: if the model misbehaves, show the markdown plainly."""
    return EnrichResult(
        markdown=markdown,
        a2ui=A2UINode(
            type=WidgetType.CARD,
            children=[A2UINode(type=WidgetType.MARKDOWN, props={"markdown": markdown})],
        ),
    )


def enrich(markdown: str) -> EnrichResult:
    """Transform arbitrary markdown into {cleaned markdown, A2UI tree}."""
    # Offline demo: run the full app with no API key (A2UI_DEMO=1).
    if os.getenv("A2UI_DEMO"):
        from app.agent.demo import DEMO
        return DEMO

    kwargs = {
        "model": MODEL,
        "messages": build_messages(markdown),
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }
    # Ollama (and other local providers) need an explicit api_base.
    if MODEL.startswith("ollama"):
        kwargs["api_base"] = API_BASE

    try:
        resp = litellm.completion(**kwargs)
        raw = resp["choices"][0]["message"]["content"]
        data = json.loads(raw)
        return EnrichResult.model_validate(data)  # catalog + shape enforced here
    except (json.JSONDecodeError, ValidationError, KeyError, Exception):
        return _fallback(markdown)
