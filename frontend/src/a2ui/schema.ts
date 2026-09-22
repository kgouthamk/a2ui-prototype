import { z } from "zod";

// Mirror of backend/app/schema/a2ui.py. Keep the two in sync — test_contract.py
// asserts the catalogs match, because Zod strips unknown fields rather than
// erroring, so drift between them would otherwise be silent.
export const WIDGET_TYPES = [
  "Card",
  "Section",
  "List",
  "Stepper",
  "Accordion",
  "Table",
  "KeyValueList",
  "ChipGroup",
  "Grid",
  "Heading",
  "Text",
  "MarkdownBlock",
  "Alert",
  "Divider",
  // Interactive
  "Button",
  "TextField",
  "Select",
  "Checkbox",
  "Switch",
] as const;

export type WidgetType = (typeof WIDGET_TYPES)[number];

/** Widgets that read/write form state, keyed by props.name. */
export const INTERACTIVE: ReadonlySet<WidgetType> = new Set<WidgetType>([
  "Button",
  "TextField",
  "Select",
  "Checkbox",
  "Switch",
]);

export interface A2UINode {
  type: WidgetType;
  props: Record<string, unknown>;
  children: A2UINode[];
  /** Dispatched on interaction. The server only honors this on Button. */
  action?: string | null;
}

// Input type is `unknown`, not A2UINode: `props`/`children` have .default(), so
// they are optional on the way IN and guaranteed on the way OUT. Annotating both
// sides as A2UINode makes the two disagree and fails the build.
export const A2UINodeSchema: z.ZodType<A2UINode, z.ZodTypeDef, unknown> = z.lazy(() =>
  z.object({
    type: z.enum(WIDGET_TYPES),
    props: z.record(z.unknown()).default({}),
    children: z.array(A2UINodeSchema).default([]),
    action: z.string().nullish(),
  })
);

export const EnrichResultSchema = z.object({
  markdown: z.string(),
  a2ui: A2UINodeSchema,
});

export type EnrichResult = z.infer<typeof EnrichResultSchema>;
