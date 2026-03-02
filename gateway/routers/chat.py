"""Proxy /v1/chat/completions and /v1/models to LiteLLM."""

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..auth import authenticate
from ..config import Settings, get_settings

router = APIRouter(prefix="/v1")


@router.get("/models")
async def list_models(
    _caller: dict = Depends(authenticate),
    settings: Settings = Depends(get_settings),
):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{settings.litellm_url}/v1/models")
        return r.json()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    _caller: dict = Depends(authenticate),
    settings: Settings = Depends(get_settings),
):
    body = await request.body()

    async with httpx.AsyncClient(timeout=300) as client:
        r = await client.post(
            f"{settings.litellm_url}/v1/chat/completions",
            content=body,
            headers={"Content-Type": "application/json"},
        )

        # If LiteLLM returned a streaming response, stream it through
        if r.headers.get("transfer-encoding") == "chunked":
            return StreamingResponse(
                r.aiter_bytes(),
                media_type=r.headers.get("content-type", "text/event-stream"),
            )

        return r.json()
