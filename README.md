# A2UI Prototype

Paste arbitrary **Markdown** into a chat UI; an agent returns **(1) cleaned
markdown** and **(2) a declarative A2UI JSON tree** rendered into **Material
Design widgets**.

```
Markdown ──POST /api/enrich──► FastAPI ──agent.enrich()──► LiteLLM (free cloud model)
                                                              │ structured JSON
                                                              ▼
        MUI widgets ◄── Renderer+Registry ◄── Zod validate ◄── { markdown, a2ui }
```

## Stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite |
| UI system | MUI (Material Design) |
| Agent | FastAPI + LiteLLM (single structured-output call) |
| Model | Free cloud inference (Groq default; Gemini / OpenRouter alt) |
| A2UI | Constrained JSON tree + client registry + recursive renderer |
| Evals | pytest (deterministic gate) + Promptfoo (prompt/model + judge) |

## The one architectural rule

The web layer (`app/main.py`) **never imports the model client** — it only calls
`agent.enrich()`. That single seam is what makes swapping LiteLLM for **Google
ADK** later a one-file change; the schema, prompt, API, and frontend are untouched.

## Run it

**1. Get a free key** (no card): https://console.groq.com/keys

**2. Backend**
```bash
cd backend
cp .env.example .env          # paste your GROQ_API_KEY
pip install -e .              # or: pip install fastapi "uvicorn[standard]" litellm pydantic sse-starlette python-dotenv
uvicorn app.main:app --reload # http://localhost:8000
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

Change the model anytime by editing one line in `backend/.env` (Groq → Gemini →
OpenRouter → local Ollama). LiteLLM handles the rest.

## Examples to test with

[EXAMPLES.md](EXAMPLES.md) has ready-to-paste inputs for every widget, including
the interactive forms, plus what each one should produce and how to read a
fallback in the backend log.

## How to control which widgets get used

Three layers, by design:

1. **What's allowed** — the `WidgetType` enum in `backend/app/schema/a2ui.py`.
   The model literally cannot emit a type outside it. It's injected into the prompt.
2. **How it's chosen** — the widget guide + selection rules in
   `backend/app/agent/prompt.py`.
3. **How it renders** — `frontend/src/a2ui/registry.tsx` maps `type → MUI component`.

**Add a widget = 3 edits:** add to the enum, describe it in the prompt, add a
registry entry. Unknown types route to a safe `FallbackNode` — the UI never crashes.

## Evals

Deterministic gate (free, offline, always in CI):
```bash
cd evals/pytest && pip install pytest && pytest -q
```

Prompt/model + LLM-as-judge (faithfulness, widget appropriateness):
```bash
cd evals && GROQ_API_KEY=... npx promptfoo@latest eval && npx promptfoo@latest view
```

**Why this split:** the output is structured JSON, so the failures that break the
UI (invalid schema, off-catalog widgets, fabrication) are best caught by cheap
deterministic assertions. The LLM-judge layer covers the fuzzy remainder. For
long-term tracking, wire scores into Langfuse (already in your stack) rather than
adding a new platform.

## Layout

```
backend/   FastAPI + agent seam + Pydantic A2UI schema
frontend/  Vite + MUI renderer + registry + chat
evals/     pytest gate + Promptfoo harness
```
