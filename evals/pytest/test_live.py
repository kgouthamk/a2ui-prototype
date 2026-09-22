"""Live eval — calls the real agent. Skipped automatically unless a model key is
set, so the offline gate stays green in CI while this runs on demand.

Run:  cd evals/pytest && GROQ_API_KEY=... pytest test_live.py -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

HAS_KEY = any(
    os.getenv(k) for k in ("GROQ_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY")
)

pytestmark = pytest.mark.skipif(not HAS_KEY, reason="no model API key set")

from app.agent import enrich  # noqa: E402
from app.schema.a2ui import WidgetType  # noqa: E402

ALLOWED = {w.value for w in WidgetType}


def _walk(node, acc):
    acc.append(node.type.value)
    for c in node.children:
        _walk(c, acc)


def test_live_output_is_valid_and_on_catalog():
    result = enrich("Pricing: Basic $10, Pro $30. Warning: no refunds.")
    types: list = []
    _walk(result.a2ui, types)
    assert all(t in ALLOWED for t in types), types
    assert result.markdown.strip()


def test_live_empty_input_does_not_crash():
    result = enrich("")  # should return the graceful fallback, not raise
    assert result.a2ui.type == WidgetType.CARD
