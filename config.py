"""
에이전트별 LLM 설정 및 프로젝트 상수

Ollama OpenAI-compatible API (http://localhost:11434/v1) 사용
"""

import os
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 경로 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_ROOT = Path(__file__).parent
DEV_REPO = PROJECT_ROOT / "dev_repo"
SNAPSHOT_DIR = PROJECT_ROOT / "shared"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Ollama 연결
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_API_V1 = f"{OLLAMA_BASE_URL}/v1"
OLLAMA_API_KEY = "ollama"  # 로컬이므로 임의값

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 에이전트별 LLM config_list
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARCHITECT_CONFIG = {
    "config_list": [
        {
            "model": "qwen3-coder-next:q4_K_M",
            "base_url": OLLAMA_API_V1,
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.3,
    "cache_seed": None,  # 캐시 비활성화 (매번 새로운 응답)
}

CODER_CONFIG = {
    "config_list": [
        {
            "model": "qwen3-coder:30b",
            "base_url": OLLAMA_API_V1,
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.2,
    "cache_seed": None,
}

REVIEWER_CONFIG = {
    "config_list": [
        {
            "model": "qwen3:14b",
            "base_url": OLLAMA_API_V1,
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.3,
    "cache_seed": None,
}

TESTER_CONFIG = {
    "config_list": [
        {
            "model": "qwen3:14b",
            "base_url": OLLAMA_API_V1,
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.2,
    "cache_seed": None,
}

ROUTER_CONFIG = {
    "config_list": [
        {
            "model": "qwen2.5:7b",
            "base_url": OLLAMA_API_V1,
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.3,
    "cache_seed": None,
}

DOCUMENTER_CONFIG = ROUTER_CONFIG  # Router와 동일 모델 공유

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Docker 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCKER_IMAGE = "python:3.11-slim"
DOCKER_WORK_DIR = "/app"
DOCKER_NETWORK_DISABLED = True  # 보안: 네트워크 차단

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 워크플로우 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAX_TDD_RETRIES = 5       # TDD 루프 최대 반복
MAX_REVIEW_RETRIES = 2    # 코드 리뷰 최대 반복
GROUPCHAT_MAX_ROUND = 15  # GroupChat 최대 라운드

# Router API (router.py FastAPI 서버)
ROUTER_API_URL = os.getenv("ROUTER_API", "http://localhost:8000")
