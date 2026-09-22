"""FastAPI app. NOTE: this file does not import litellm or any model client.
It only calls agent.enrich() — that is the ADK-migration seam.
"""
from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app import agent

app = FastAPI(title="A2UI Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnrichRequest(BaseModel):
    markdown: str


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/enrich")
async def enrich_endpoint(req: EnrichRequest) -> EventSourceResponse:
    async def stream():
        # enrich() is sync/blocking; run it off the event loop.
        result = await asyncio.to_thread(agent.enrich, req.markdown)
        yield {"event": "result", "data": result.model_dump_json()}

    return EventSourceResponse(stream())
