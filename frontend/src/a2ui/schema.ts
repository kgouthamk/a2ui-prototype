import { z } from "zod";

// Mirror of backend/app/schema/a2ui.py. Keep the two in sync.
export const WIDGET_TYPES = [
  "Card",
  "Section",
  "List",
  "Stepper",
  "Accordion",
  "Table",
  "KeyValueList",
  "ChipGroup",
  "Heading",
  "Text",
  "MarkdownBlock",
  "Alert",
  "Divider",
] as const;

export type WidgetType = (typeof WIDGET_TYPES)[number];

export interface A2UINode {
  type: WidgetType;
  props: Record<string, unknown>;
  children: A2UINode[];
}

// Input type is `unknown`, not A2UINode: `props`/`children` have .default(), so
// they are optional on the way IN and guaranteed on the way OUT. Annotating both
// sides as A2UINode makes the two disagree and fails the build.
export const A2UINodeSchema: z.ZodType<A2UINode, z.ZodTypeDef, unknown> = z.lazy(() =>
  z.object({
    type: z.enum(WIDGET_TYPES),
    props: z.record(z.unknown()).default({}),
    children: z.array(A2UINodeSchema).default([]),
  })
);

export const EnrichResultSchema = z.object({
  markdown: z.string(),
  a2ui: A2UINodeSchema,
});

export type EnrichResult = z.infer<typeof EnrichResultSchema>;
