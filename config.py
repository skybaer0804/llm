"""
LLM 설정 및 프로젝트 상수

Thunderbolt 분산 아키텍처:
- Gateway: llama3.1:8b (MacBook, 24GB) - 라우팅 분석 전용
- Worker:  qwen3-coder-next:q4_K_M (Mac Mini, 64GB) - 모든 에이전트 공유
"""

import os
import re
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 경로 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT_ROOT = Path(__file__).parent
DEV_REPO = PROJECT_ROOT / "dev_repo"
SNAPSHOT_DIR = PROJECT_ROOT / "shared"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Ollama 연결 (Thunderbolt 분산)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MACBOOK_OLLAMA = os.getenv("MACBOOK_OLLAMA", "http://localhost:11434")
MACMINI_OLLAMA = os.getenv("MACMINI_OLLAMA", "http://127.0.0.1:11434")
OLLAMA_API_KEY = "ollama"  # 로컬이므로 임의값

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM 모델 설정 (Thunderbolt 분산 아키텍처)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 작업 모델 - 모든 에이전트가 공유 (Mac Mini, 52GB)
MAIN_MODEL = "qwen3-coder-next:q4_K_M"
MAIN_LLM_CONFIG = {
    "config_list": [
        {
            "model": MAIN_MODEL,
            "base_url": f"{MACMINI_OLLAMA}/v1",
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.3,
    "cache_seed": None,
}

# 게이트웨이 모델 - 라우터 분석 전용 (MacBook, 상시 상주)
GATEWAY_MODEL = "llama3.1:8b"
GATEWAY_LLM_CONFIG = {
    "config_list": [
        {
            "model": GATEWAY_MODEL,
            "base_url": f"{MACBOOK_OLLAMA}/v1",
            "api_key": OLLAMA_API_KEY,
            "api_type": "openai",
        }
    ],
    "temperature": 0.3,
    "cache_seed": None,
}

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLAUDE.md 규칙 로드 및 시스템 지침
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def load_claude_rules():
    """CLAUDE.md에서 Global Rules 섹션만 추출하여 경량화된 규칙 반환"""
    claude_md_path = PROJECT_ROOT / "CLAUDE.md"

    if not claude_md_path.exists():
        return ""

    try:
        with open(claude_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Global Rules 섹션만 추출 (컨텍스트 절약)
        match = re.search(
            r"(## 🤖 Global Rules.*?)(?=\n## |\Z)",
            content,
            re.DOTALL,
        )
        if match:
            rules_text = match.group(1).strip()
        else:
            # 섹션 추출 실패 시 전체 주입하되 길이 제한
            rules_text = content[:1500]

        return f"\n=== PROJECT RULES ===\n{rules_text}\n=====================\n"
    except Exception as e:
        return f"Error reading CLAUDE.md: {str(e)}"


BASE_INSTRUCTION = """당신은 M4 Pro macOS 환경에 최적화된 전문 소프트웨어 엔지니어 에이전트입니다.

[환경 정보]
- OS: macOS (Apple Silicon M4 Pro)
- Python: 3.12
- 가상환경: .venv (venv)
- 작업 디렉토리: dev_repo/ 내에서 파일 생성
- 테스트 프레임워크: pytest

[핵심 규칙]
1. TDD-First: 테스트 코드를 먼저 작성하고, 기능 코드를 나중에 작성한다.
2. YAGNI: 최소한의 코드로 요구사항을 충족시킨다. 불필요한 추상화 금지.
3. 보안: eval/exec 금지, 외부 URL 접속 금지, 민감 정보 하드코딩 금지.
"""
