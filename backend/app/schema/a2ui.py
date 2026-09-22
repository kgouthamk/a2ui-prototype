"""A2UI schema — the model-agnostic contract shared by agent, API, and client.

This is the single source of truth for what widgets the LLM may emit.
Add a widget here (WidgetType) + describe it in prompt.py + register it in the
frontend registry. Nothing else needs to change.

Keep this in sync with frontend/src/a2ui/schema.ts — test_contract.py asserts the
two catalogs match, because Zod strips unknown fields rather than erroring and
drift between them would otherwise be silent.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


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
    # Interactive. These read/write client state via props.name; Button also
    # carries `action`, which is what gets POSTed back to /api/action.
    BUTTON = "Button"
    TEXT_FIELD = "TextField"
    SELECT = "Select"
    CHECKBOX = "Checkbox"
    SWITCH = "Switch"


#: Widgets whose `action` the client actually dispatches. An `action` anywhere else
#: would render a control that looks live and does nothing, so it is stripped.
ACTIONABLE = frozenset({WidgetType.BUTTON})

#: Widgets that participate in form state (their props.name keys the value map).
INTERACTIVE = frozenset(
    {
        WidgetType.BUTTON,
        WidgetType.TEXT_FIELD,
        WidgetType.SELECT,
        WidgetType.CHECKBOX,
        WidgetType.SWITCH,
    }
)


class A2UINode(BaseModel):
    """A declarative UI node. `props` are widget-specific; `children` nest."""

    type: WidgetType
    props: dict[str, Any] = Field(default_factory=dict)
    children: list["A2UINode"] = Field(default_factory=list)
    action: str | None = Field(
        default=None,
        description="Action id dispatched on interaction. Only honored on Button.",
    )

    @model_validator(mode="after")
    def _strip_unhonored_action(self) -> "A2UINode":
        """Drop an `action` the client would never dispatch — but say so.

        Rejecting the whole tree over one stray field would throw away an otherwise
        good response and fall back to plain markdown. Dropping it keeps the tree
        renderable; the log line is what stops it being a silent no-op.
        """
        if self.action is not None and self.type not in ACTIONABLE:
            logger.warning(
                "a2ui: dropping action=%r on %s — only %s dispatch actions",
                self.action,
                self.type.value,
                ", ".join(sorted(w.value for w in ACTIONABLE)),
            )
            object.__setattr__(self, "action", None)
        return self


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
        'Node = { "type": WidgetType, "props": object, "children": Node[],\n'
        '         "action"?: string }\n'
        f"WidgetType is one of: {catalog}\n"
    )
