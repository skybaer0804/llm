"""LLM Gateway — single entry point for all LLM services."""

from fastapi import FastAPI

from .config import get_settings
from .routers import chat, health, tasks

settings = get_settings()

app = FastAPI(
    title="LLM Gateway",
    description="Unified API gateway for LLM services",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    return {
        "service": "LLM Gateway",
        "version": "1.0.0",
        "endpoints": ["/health", "/v1/models", "/v1/chat/completions", "/v1/tasks"],
    }
