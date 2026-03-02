import psutil
import httpx
from fastapi import APIRouter, Depends

from ..config import Settings, get_settings

router = APIRouter()


@router.get("/health")
async def health(settings: Settings = Depends(get_settings)):
    mem = psutil.virtual_memory()
    services = {}

    async with httpx.AsyncClient(timeout=3) as client:
        # Ollama
        try:
            r = await client.get(f"{settings.ollama_url}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            services["ollama"] = {"status": "ok", "models": models}
        except Exception:
            services["ollama"] = {"status": "down"}

        # LiteLLM
        try:
            r = await client.get(f"{settings.litellm_url}/v1/models")
            model_ids = [m["id"] for m in r.json().get("data", [])]
            services["litellm"] = {"status": "ok", "models": model_ids}
        except Exception:
            services["litellm"] = {"status": "down"}

    all_ok = all(s["status"] == "ok" for s in services.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "services": services,
        "memory": {
            "total_gb": round(mem.total / (1024**3), 1),
            "available_gb": round(mem.available / (1024**3), 1),
            "percent_used": mem.percent,
        },
    }
