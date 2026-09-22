import { EnrichResult, EnrichResultSchema } from "../a2ui/schema";

// In production the SPA and the API share one Vercel domain (see vercel.json's
// rewrites), so "" makes every call same-origin and CORS never comes into play.
// Locally they are on different ports, hence the dev default.
const API =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.PROD ? "" : "http://localhost:8000");

/** Read the single SSE `result` event from a POST, validate it, return it. */
async function postForResult(path: string, body: unknown): Promise<EnrichResult> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);

  // Minimal SSE parse: accumulate, grab the `data:` line of the result event.
  const text = await res.text();
  const line = text
    .split("\n")
    .find((l) => l.startsWith("data:"));
  if (!line) throw new Error(`${path}: no result event in response`);

  return EnrichResultSchema.parse(JSON.parse(line.slice(5).trim()));
}

/** POST markdown, get back {cleaned markdown, A2UI tree}. */
export function enrich(markdown: string): Promise<EnrichResult> {
  return postForResult("/api/enrich", { markdown });
}

/**
 * Dispatch a UI action. `markdown` is the original source document, echoed back so
 * the agent has the facts — the server keeps no session.
 */
export function sendAction(
  action: string,
  values: Record<string, unknown>,
  markdown: string
): Promise<EnrichResult> {
  return postForResult("/api/action", { action, values, markdown });
}
