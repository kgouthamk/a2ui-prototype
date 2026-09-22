"""Live eval — calls the real agent. Skipped automatically unless a model key is
set, so the offline gate stays green in CI while this runs on demand.

Run:  cd evals/pytest && pytest test_live.py -q
(the key is read from backend/.env, or from the environment if exported)
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

# Import first: this is what loads backend/.env. Checking for a key before the
# import made these tests skip silently whenever the key lived only in .env.
from app.agent import enrich  # noqa: E402
from app.schema.a2ui import WidgetType  # noqa: E402

HAS_KEY = any(
    os.getenv(k) for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY")
)

pytestmark = pytest.mark.skipif(not HAS_KEY, reason="no model API key set")

ALLOWED = {w.value for w in WidgetType}

SAMPLE = "Pricing: Basic $10, Pro $30. Warning: no refunds."


def _walk(node, acc):
    acc.append(node.type.value)
    for c in node.children:
        _walk(c, acc)


@pytest.fixture
def strict(monkeypatch):
    """Make the agent raise instead of falling back.

    Without this, a dead key returns Card > MarkdownBlock — which satisfies every
    "is it on catalog?" assertion below. The suite would go green while the model
    was never reached.
    """
    monkeypatch.setenv("A2UI_STRICT", "1")


def test_live_output_is_valid_and_on_catalog(strict):
    result = enrich(SAMPLE)
    types: list = []
    _walk(result.a2ui, types)
    assert all(t in ALLOWED for t in types), types
    assert result.markdown.strip()


def test_live_response_is_not_the_fallback(strict):
    """Guard the specific shape the fallback emits, so it can never score as a pass."""
    result = enrich(SAMPLE)
    types: list = []
    _walk(result.a2ui, types)
    assert types != ["Card", "MarkdownBlock"], "got the fallback tree, not model output"
    assert result.markdown.strip() != SAMPLE.strip(), "markdown echoed input verbatim"


def test_live_empty_input_does_not_crash():
    # No `strict` here: this test is specifically about degrading gracefully.
    result = enrich("")
    assert result.a2ui.type == WidgetType.CARD
