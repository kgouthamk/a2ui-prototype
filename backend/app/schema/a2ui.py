"""A2UI schema — the model-agnostic contract shared by agent, API, and client.

This is the single source of truth for what widgets the LLM may emit.
Add a widget here (WidgetType) + describe it in prompt.py + register it in the
frontend registry. Nothing else needs to change.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WidgetType(str, Enum):
    """The catalog. The LLM CANNOT emit a type outside this whitelist."""

    # Containers
    CARD = "Card"
    SECTION = "Section"
    LIST = "List"
    STEPPER = "Stepper"
    ACCORDION = "Accordion"
    TABLE = "Table"
    KEY_VALUE_LIST = "KeyValueList"
    CHIP_GROUP = "ChipGroup"
    # Leaves
    HEADING = "Heading"
    TEXT = "Text"
    MARKDOWN = "MarkdownBlock"
    ALERT = "Alert"
    DIVIDER = "Divider"


class A2UINode(BaseModel):
    """A declarative UI node. `props` are widget-specific; `children` nest."""

    type: WidgetType
    props: dict[str, Any] = Field(default_factory=dict)
    children: list["A2UINode"] = Field(default_factory=list)


A2UINode.model_rebuild()


class EnrichResult(BaseModel):
    """The envelope the agent returns and the API streams to the client."""

    markdown: str = Field(description="Cleaned / reformatted markdown.")
    a2ui: A2UINode = Field(description="Root A2UI node (usually a Card or Section).")


def json_schema_for_prompt() -> str:
    """Compact schema text injected into the system prompt."""
    catalog = ", ".join(w.value for w in WidgetType)
    return (
        "Return ONLY JSON matching:\n"
        '{ "markdown": string, "a2ui": Node }\n'
        'Node = { "type": WidgetType, "props": object, "children": Node[] }\n'
        f"WidgetType is one of: {catalog}\n"
    )
