"""FastAPI app. NOTE: this file does not import litellm or any model client.
It only calls agent.enrich() / agent.act() — that is the ADK-migration seam.
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app import agent

# uvicorn only attaches handlers to its own loggers, so app-level logs are dropped
# by default. The agent logs WHY it fell back — that needs to reach the terminal.
# force=True because basicConfig is a no-op once any import has claimed the root
# logger — litellm is imported (via app.agent) before this line runs.
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s",
                    force=True)

app = FastAPI(title="A2UI Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnrichRequest(BaseModel):
    markdown: str


class ActionRequest(BaseModel):
    """A UI action dispatched by the client.

    `markdown` is the original source document, echoed back by the client. The
    server holds no session: the client owns the context, which keeps this endpoint
    as stateless as /api/enrich.
    """

    action: str
    values: dict[str, object] = Field(default_factory=dict)
    markdown: str


@app.get("/health")
def health() -> dict:
    return {"ok": True}


def _sse(result_fn) -> EventSourceResponse:
    """Both endpoints stream the same single `result` event holding an EnrichResult."""

    async def stream():
        # The agent is sync/blocking; run it off the event loop.
        result = await asyncio.to_thread(result_fn)
        yield {"event": "result", "data": result.model_dump_json()}

    return EventSourceResponse(stream())


@app.post("/api/enrich")
async def enrich_endpoint(req: EnrichRequest) -> EventSourceResponse:
    return _sse(lambda: agent.enrich(req.markdown))


@app.post("/api/action")
async def action_endpoint(req: ActionRequest) -> EventSourceResponse:
    return _sse(lambda: agent.act(req.markdown, req.action, req.values))
