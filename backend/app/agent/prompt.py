"""Prompt construction — this is where widget SELECTION is steered.

Change these descriptions to change how the model chooses widgets.
Keep it tight; this text ships on every request.
"""
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

Selection rules:
- Tabular / comparison content -> Table.
- Numbered or sequential steps / how-to -> Stepper.
- Warnings, notes, tips, cautions -> Alert with the matching severity.
- Key facts, specs, metadata pairs -> KeyValueList.
- Tags, keywords, categories -> ChipGroup.
- FAQ or long optional detail -> Accordion.
- Prefer 1 Card at the root containing a few well-chosen widgets.
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


def build_messages(markdown: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": markdown},
    ]
