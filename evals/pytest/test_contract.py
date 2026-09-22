"""Deterministic, offline eval gate — NO model, NO network, NO key required.
Always runs in CI. This is the workhorse: it proves the A2UI contract holds and
that malformed payloads degrade instead of crashing.

Run:  cd evals/pytest && pip install pytest && pytest -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.schema.a2ui import A2UINode, EnrichResult, WidgetType  # noqa: E402

ALLOWED = {w.value for w in WidgetType}


def walk_types(node: dict, acc: list) -> None:
    acc.append(node["type"])
    for c in node.get("children", []) or []:
        walk_types(c, acc)


# A hand-authored "golden" payload representing a good agent output.
GOLDEN = {
    "markdown": "# Deploy\n\n1. Build\n2. Push\n3. Roll out\n",
    "a2ui": {
        "type": "Card",
        "props": {},
        "children": [
            {"type": "Heading", "props": {"text": "Deploy", "level": 4}, "children": []},
            {
                "type": "Stepper",
                "props": {"steps": [{"label": "Build", "detail": ""}]},
                "children": [],
            },
        ],
    },
}


def test_golden_payload_is_valid_envelope():
    result = EnrichResult.model_validate(GOLDEN)
    assert result.markdown
    assert result.a2ui.type == WidgetType.CARD


def test_all_widget_types_on_catalog():
    types: list = []
    walk_types(GOLDEN["a2ui"], types)
    assert all(t in ALLOWED for t in types), types


def test_off_catalog_type_is_rejected():
    bad = {
        "markdown": "x",
        "a2ui": {"type": "Iframe", "props": {}, "children": []},
    }
    with pytest.raises(Exception):
        EnrichResult.model_validate(bad)


def test_nested_children_recurse():
    node = A2UINode.model_validate(
        {
            "type": "Card",
            "props": {},
            "children": [
                {"type": "Section", "props": {"title": "A"}, "children": [
                    {"type": "Text", "props": {"text": "hi"}, "children": []}
                ]}
            ],
        }
    )
    assert node.children[0].children[0].type == WidgetType.TEXT


# --- contract parity + the action field -------------------------------------

SCHEMA_TS = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "src", "a2ui", "schema.ts"
)


def test_python_and_typescript_catalogs_match():
    """The two schemas ARE the contract, and drift between them is silent.

    Zod strips unknown fields rather than erroring, so a widget added on one side
    only would render as a FallbackNode (or vanish) with nothing failing.
    """
    import re

    src = open(SCHEMA_TS).read()
    block = re.search(r"WIDGET_TYPES = \[(.*?)\] as const", src, re.S)
    assert block, "could not find WIDGET_TYPES in schema.ts"
    ts = set(re.findall(r'"(\w+)"', block.group(1)))
    py = {w.value for w in WidgetType}
    assert ts == py, f"only in TS: {ts - py} | only in Python: {py - ts}"


def test_action_is_kept_on_button():
    node = A2UINode.model_validate(
        {"type": "Button", "props": {"label": "Go"}, "action": "submit_claim"}
    )
    assert node.action == "submit_claim"


def test_action_is_dropped_from_non_actionable_widgets():
    # Rendering a control that looks live but dispatches nothing is the failure
    # mode this guards; the agent logs a warning when it strips one.
    node = A2UINode.model_validate(
        {"type": "Text", "props": {"text": "hi"}, "action": "submit_claim"}
    )
    assert node.action is None


def test_interactive_widgets_are_on_the_catalog():
    for w in ("Button", "TextField", "Select", "Checkbox", "Switch"):
        assert w in ALLOWED
