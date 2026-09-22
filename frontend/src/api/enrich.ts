import { EnrichResult, EnrichResultSchema } from "../a2ui/schema";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** POST markdown, read the single SSE `result` event, validate, return it. */
export async function enrich(markdown: string): Promise<EnrichResult> {
  const res = await fetch(`${API}/api/enrich`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ markdown }),
  });
  if (!res.ok || !res.body) throw new Error(`Request failed: ${res.status}`);

  // Minimal SSE parse: accumulate, grab the `data:` line of the result event.
  const text = await res.text();
  const dataLine = text
    .split("\n")
    .find((l) => l.startsWith("data:"));
  if (!dataLine) throw new Error("No data in response");

  const json = JSON.parse(dataLine.slice("data:".length).trim());
  return EnrichResultSchema.parse(json);
}
