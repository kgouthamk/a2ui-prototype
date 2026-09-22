# Adopting this pattern with your own design system

This repo renders its widgets with [MUI](https://mui.com). Almost none of it is
MUI-specific. This is what to change, in what order, and the traps that cost this
project real time — so you can tell Claude Code about them up front instead of
rediscovering them.

## What actually changes

The widget catalog lives in three places by design:

| Layer | File | Design-system specific? |
|---|---|---|
| What the model MAY emit | `backend/app/schema/a2ui.py` (`WidgetType`) | No — but see below |
| When to choose each one | `backend/app/agent/prompt.py` | No |
| How each one DRAWS | `frontend/src/a2ui/registry.tsx` | **Yes — this is the whole job** |

The agent, the schema, the API and the recursive renderer never import MUI. Swapping
design systems is essentially "keep the contract, rewrite the registry".

The trap is assuming the catalog carries over too. It should not. Derive it from what
**your** system actually has. If you have a `DataTable` and a `StatusPill` but no
accordion, the enum should say so. A widget in the catalog with no component behind it
is a fallback node waiting to happen.

## A starter prompt

```
I'm building a PoC: paste arbitrary Markdown into a chat UI, an agent returns
(1) cleaned markdown and (2) a declarative JSON UI tree that gets rendered as
components from our design system.

Our design system: <package name / path / Storybook URL>

Start by reading our design system and proposing a widget catalog — 10-15
component types that cover the shapes markdown actually takes (facts, tabular
data, ordered steps, callouts, tags, collapsible detail). For each, tell me
which of our components it maps to. Do NOT invent components we don't have,
and flag any common markdown shape our system can't express.

Architecture I want:
- FastAPI + LiteLLM, one structured-output call, behind a single function
  `enrich(markdown) -> EnrichResult`. The web layer must never import the
  model client, so the agent can be swapped later without touching anything else.
- The catalog is a hard whitelist, validated server-side with Pydantic and
  client-side with Zod. Unknown types render a visible fallback node, never crash.
- React + Vite client with a recursive renderer and a type -> component registry.

Don't write code yet. Propose the catalog and the file layout first.
```

Making it propose the catalog *before* writing code matters. The catalog is the
contract, and it is the expensive thing to change later.

## Then, in order

1. **"Scaffold it, deterministic offline tests first"** — schema validation, catalog
   enforcement, fallback behaviour. No model calls. This suite is your gate and it
   should stay free to run.
2. **"Wire up the real model. Before judging any output, prove the model is actually
   reachable."** Not optional. See below.
3. **"Add a test asserting the Python enum and the TypeScript array contain the same
   members."** Zod strips unknown fields rather than erroring, so drift between the
   two schemas is silent.
4. **"Now tune the prompt for widget selection."** Only now — before this point you
   cannot distinguish a bad prompt from a broken pipeline.

## Five things to tell Claude up front

Each of these cost this project real time.

### 1. Never catch bare `Exception` around the model call

The original `enrich()` had `except (json.JSONDecodeError, ValidationError, KeyError,
Exception)` and returned a graceful fallback with no log. An invalid API key was
therefore indistinguishable from the model choosing boring widgets — and got filed as
a prompt-engineering problem in the handoff doc. It was not.

Ask for: a separate catch per stage (call / response shape / JSON parse / schema
validation), each logging the model name and the real error, plus a strict mode
(`A2UI_STRICT=1` here) that raises instead of falling back.

### 2. Make the fallback visually distinct from a real response

The fallback rendered the input markdown verbatim inside a card — plausible enough
that nobody questioned it. If your fallback is indistinguishable from success, every
failure becomes a wild goose chase. Consider surfacing a degraded flag in the payload
and rendering a banner.

### 3. Never let a test pass on the fallback

The live tests asserted "every widget type is on the catalog" and "markdown is
non-empty". The fallback satisfies both. Green suite, dead model.

Assert against the *specific shape* the fallback emits, and run live tests under
strict mode.

### 4. Expect model names to be retired

`gemini-2.0-flash` and every Groq Llama chat model returned 404 during this project —
same failure shape each time: the key authenticates, the model name does not exist,
and the result is the silent fallback. Ask for `NotFoundError` to be surfaced loudly,
and check the provider's `/models` endpoint rather than trusting a name in a config.

### 5. Verify against the real thing, not a proxy

`KeyValueList` rendered key and value inverted for as long as the code existed,
because every real request was falling back to a different widget and that renderer
had never run. `npm run build` had never passed either — only `vite dev` was ever
used, and it does not typecheck.

Ask for a real end-to-end pass — real model, real browser — before calling anything
done.

## Two more things worth planning for

**Provider JSON reliability.** Groq's constrained-JSON decoder rejected its own output
on roughly a third of large trees (`json_validate_failed`). The model produced a
perfectly good tree; the provider refused it. Budget for retries on the provider's
bad-request errors — but not on auth, quota or not-found, where an immediate retry
just burns another request against the same wall.

**Free-tier quota is smaller than you think.** Gemini AI Studio allows 20 requests per
day per model. A single test-suite run here costs 3. If you deploy a public demo on a
personal key, most visitors will see the fallback.

## If your design system lives in Figma

Claude Code's Figma MCP tools (`search_design_system`, `get_design_context`) can
bootstrap the catalog from the actual component library rather than from a written
description of it. Untested here, but it is the right first thing to try before
hand-writing an enum.
