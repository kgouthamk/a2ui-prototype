import type { ReactNode } from "react";
import Alert from "@mui/material/Alert";
import { registry } from "./registry";
import { A2UINode, A2UINodeSchema } from "./schema";

/** A node whose `type` isn't in the registry -> shown, never crashes. */
function FallbackNode({ type }: { type: string }) {
  return (
    <Alert severity="warning" sx={{ my: 1 }}>
      Unknown widget: <code>{type}</code>
    </Alert>
  );
}

function renderNode(node: A2UINode, key: number): ReactNode {
  const children = (node.children ?? []).map((c, i) => renderNode(c, i));
  const render = registry[node.type];
  if (!render) return <FallbackNode key={key} type={node.type} />;
  return <div key={key}>{render(node.props ?? {}, children, node.action)}</div>;
}

/** Validate the tree, then render it. Invalid payloads degrade gracefully. */
export function Renderer({ node }: { node: unknown }) {
  const parsed = A2UINodeSchema.safeParse(node);
  if (!parsed.success) {
    return (
      <Alert severity="error">
        A2UI payload failed validation — check the agent output.
      </Alert>
    );
  }
  return <>{renderNode(parsed.data, 0)}</>;
}
