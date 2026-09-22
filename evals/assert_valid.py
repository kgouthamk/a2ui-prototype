"""Deterministic assertion: does the output parse as a valid A2UI envelope with
only whitelisted widget types? This is the single most important gate for a
generative-UI system — an invalid tree can't render.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.schema.a2ui import EnrichResult, WidgetType  # noqa: E402

_ALLOWED = {w.value for w in WidgetType}


def _walk_types(node, acc):
    acc.append(node.get("type"))
    for child in node.get("children", []) or []:
        _walk_types(child, acc)


def get_assert(output, context):
    try:
        data = json.loads(output)
    except Exception as e:
        return {"pass": False, "score": 0.0, "reason": f"not JSON: {e}"}

    # Catalog conformance (before pydantic, so we can name the offender).
    types: list = []
    if isinstance(data.get("a2ui"), dict):
        _walk_types(data["a2ui"], types)
    off_catalog = [t for t in types if t not in _ALLOWED]
    if off_catalog:
        return {
            "pass": False,
            "score": 0.0,
            "reason": f"off-catalog widget types: {sorted(set(off_catalog))}",
        }

    # Shape / schema validity.
    try:
        EnrichResult.model_validate(data)
    except Exception as e:
        return {"pass": False, "score": 0.0, "reason": f"schema invalid: {e}"}

    return {"pass": True, "score": 1.0, "reason": "valid A2UI envelope"}
