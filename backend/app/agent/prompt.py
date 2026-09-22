"""Prompt construction — this is where widget SELECTION is steered.

Change these descriptions to change how the model chooses widgets.
Keep it tight; this text ships on every request.
"""
import json

from app.schema.a2ui import json_schema_for_prompt

WIDGET_GUIDE = """\
Widget catalog and when to use each:
- Card: top-level container that wraps a coherent block. Use as the root.
- Section: a titled sub-group inside a Card. props: { "title": string }
- Heading: a title line. props: { "text": string, "level": 1-6 }
- Text: a short paragraph of plain text. props: { "text": string }
- MarkdownBlock: a chunk of rich markdown (lists, emphasis, code). props: { "markdown": string }
- Table: tabular data. props: { "columns": string[], "rows": string[][] }
- KeyValueList: labeled facts / metadata. props: { "items": [{ "key": string, "value": string }] }
- ChipGroup: tags, categories, keywords. props: { "chips": string[] }
- Alert: a callout. props: { "severity": "info"|"success"|"warning"|"error", "text": string }
- Stepper: an ORDERED sequence of steps. props: { "steps": [{ "label": string, "detail": string }] }
- Accordion: collapsible Q&A or long optional detail. props: { "panels": [{ "summary": string, "detail": string }] }
- List: an unordered set of items. props: { "items": string[] }
- Divider: a visual separator. props: {}
- Grid: lays its CHILDREN out side by side. Use it to show several Cards as a
  stack of cards. props: { "columns": 1-4 }  children: usually Card nodes

Interactive widgets — ONLY use these when the input asks the reader to decide,
choose, confirm, or supply something. Never invent a form for static content.
- TextField: free text entry. props: { "name": string, "label": string, "multiline"?: bool, "placeholder"?: string }
- Select: choose one of a fixed set. props: { "name": string, "label": string, "options": string[] }
- Checkbox: a single on/off choice. props: { "name": string, "label": string }
- Switch: a single on/off setting. props: { "name": string, "label": string }
- Button: submits the surrounding fields. props: { "label": string, "variant"?: "contained"|"outlined"|"text" }
  Button is the ONLY widget that may carry a top-level "action": a short
  lowercase id naming what the click does, e.g. "submit_claim", "recalculate".

Rules for interactive widgets:
- Every TextField/Select/Checkbox/Switch MUST have a unique "name".
- "action" goes on the Button and NOWHERE else — it is ignored anywhere else.
- A form needs at least one Button, or the user cannot submit it.

Selection rules:
- Tabular / comparison content -> Table.
- Numbered or sequential steps / how-to -> Stepper.
- Warnings, notes, tips, cautions -> Alert with the matching severity.
- Key facts, specs, metadata pairs -> KeyValueList.
- Tags, keywords, categories -> ChipGroup.
- FAQ or long optional detail -> Accordion.
- Prefer 1 Card at the root containing a few well-chosen widgets.
- EXCEPTION: when the content is a set of comparable items (plans, products,
  people, regions, incidents), emit one Card PER ITEM as children of a Grid, and
  make that Grid the root. Each Card gets its own Heading plus a KeyValueList or
  Text. This is the "stack of cards" layout.
- NEVER invent facts. Every value must come from the input markdown.
"""

SYSTEM_PROMPT = f"""\
You are an enrichment agent. You receive arbitrary Markdown and return two things:
1) `markdown`: the same content, cleaned and well-formatted (fix headings, lists,
   spacing, tables). Do not add or remove information.
2) `a2ui`: a declarative UI tree that presents the SAME content as rich widgets.

{WIDGET_GUIDE}

{json_schema_for_prompt()}
Output JSON only. No prose, no code fences.
"""

ACTION_PROMPT = f"""\
You are an enrichment agent handling a UI action. You receive the original source
document, the id of the action the user triggered, and the values they entered.

Return the SAME envelope as before:
1) `markdown`: the source document, updated only where the submitted values
   genuinely change it. If nothing changes, return it unchanged.
2) `a2ui`: the NEXT UI tree to display. Acknowledge what the user did — echo their
   submitted values back so they can see them recorded, and use an Alert with
   severity "success" to confirm the action.

{WIDGET_GUIDE}

{json_schema_for_prompt()}
Never invent facts: use only the source document and the submitted values.
Output JSON only. No prose, no code fences.
"""


def build_messages(markdown: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": markdown},
    ]


def build_action_messages(markdown: str, action: str, values: dict) -> list[dict]:
    payload = {
        "action": action,
        "values": values,
        "source_document": markdown,
    }
    return [
        {"role": "system", "content": ACTION_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
