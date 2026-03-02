import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gateway
    gateway_port: int = 8000
    gateway_api_keys: str = ""  # comma-separated
    gateway_jwt_secret: str = "change-me-in-production"

    # Internal services
    litellm_url: str = "http://localhost:4000"
    ollama_url: str = "http://localhost:11434"

    # External
    docs_api_url: str = "https://nodnjs-docs.koyeb.app/api"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def api_keys(self) -> set[str]:
        if not self.gateway_api_keys:
            return set()
        return {k.strip() for k in self.gateway_api_keys.split(",") if k.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
