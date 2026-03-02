# MSA Architecture Plan

> Last updated: 2026-03-02

## Overview

llm 프로젝트를 MSA 구조로 전환하여 여러 프로젝트에서 공유하고,
사용자가 직접 또는 Claude를 통해 작업을 지시할 수 있는 시스템을 구축한다.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Mac (항상 켜둠)                     │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │         LLM Gateway (:8000)                   │    │
│  │         FastAPI - 단일 진입점                   │    │
│  │                                                │    │
│  │  • JWT 인증 + API Key 인증                     │    │
│  │  • /v1/chat/completions  (LiteLLM 프록시)      │    │
│  │  • /v1/tasks             (에이전트 작업 실행)    │    │
│  │  • /health               (시스템 상태)          │    │
│  └────────────┬───────────────────────────────────┘    │
│               │                                        │
│  ┌────────────▼──────────┐   ┌─────────────────────┐  │
│  │  LiteLLM Proxy (:4000)│   │  Ollama (:11434)    │  │
│  │  OpenAI 호환 API       │──▶│  GPU 추론 (Metal)   │  │
│  │  모델 라우팅            │   │  네이티브 실행       │  │
│  └───────────────────────┘   └─────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
         │
         │ Tailscale Funnel (:8000만 외부 노출)
         ▼
┌─────────────────────────────────┐
│  외부 클라이언트                  │
│  • 다른 프로젝트 (API Key)       │
│  • Claude Code (curl)           │
│  • 사용자 직접 호출               │
│  • docs 프로젝트 (webhook)       │
└─────────────────────────────────┘
```

## Components

### 1. LLM Gateway (신규, :8000)
**역할**: 외부 유일한 진입점. 인증, 라우팅, 에이전트 실행.

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/health` | GET | 시스템 상태 (Ollama, LiteLLM, 메모리) |
| `/v1/chat/completions` | POST | LiteLLM 프록시 패스스루 (OpenAI 호환) |
| `/v1/models` | GET | 사용 가능 모델 목록 |
| `/v1/tasks` | POST | 에이전트 작업 실행 (docs-assistant 등) |
| `/v1/tasks/{id}` | GET | 작업 상태/결과 조회 |

**인증 방식**:
- API Key (`X-API-Key` 헤더) — 프로젝트 간 통신
- JWT (Bearer token) — 사용자 직접 호출

### 2. LiteLLM Proxy (기존, :4000)
- 내부 전용 (localhost만 접근)
- Gateway가 프록시로 호출
- 변경 없음

### 3. Ollama (기존, :11434)
- Metal GPU 추론 — Docker에 넣지 않음
- 네이티브 실행 유지
- 변경 없음

## Directory Structure

```
llm/
├── gateway/                 # LLM Gateway 서비스
│   ├── __init__.py
│   ├── app.py              # FastAPI 메인
│   ├── auth.py             # 인증 (API Key + JWT)
│   ├── config.py           # 설정 (환경변수)
│   ├── routers/
│   │   ├── chat.py         # /v1/chat/completions 프록시
│   │   ├── tasks.py        # /v1/tasks 에이전트 실행
│   │   └── health.py       # /health 시스템 상태
│   └── agents/
│       ├── base.py         # 에이전트 베이스 클래스
│       └── docs_agent.py   # docs-assistant (기존 로직 이관)
├── litellm/                 # LiteLLM 설정 (기존)
│   └── config.yaml
├── docker-compose.yml       # Gateway + LiteLLM 컨테이너
├── Dockerfile               # Gateway용
├── start.sh                 # 원클릭 실행 (업데이트)
├── .env                     # 환경변수
└── requirements.txt
```

## External Access Strategy

### 현재: Tailscale Funnel → LiteLLM (:4000) 직접 노출
### 변경: Tailscale Funnel → Gateway (:8000)만 노출

- LiteLLM (:4000)은 localhost 전용으로 전환
- Gateway가 인증 후 내부적으로 LiteLLM 호출
- Funnel은 Gateway 포트 하나만 노출

## Deployment Strategy

### Phase 1: 로컬 전용 (현재 목표)
- 모든 서비스가 Mac에서 실행
- Docker Compose로 Gateway + LiteLLM 관리
- Ollama는 네이티브
- 비용: 0원

### Phase 2: 클라우드 이동 준비 (코드 수준 보장)
- 서비스 간 통신: 환경변수 URL (`LITELLM_URL`, `OLLAMA_URL`)
- 각 서비스에 Dockerfile 유지
- `docker-compose.yml`로 로컬 실행, 클라우드 시 이미지만 push

### Phase 3: 선택적 클라우드 (필요시)
- Gateway만 Koyeb/Fly.io에 올리고 → Tailscale mesh로 로컬 LLM 호출
- 또는 전체를 GPU 클라우드로 이전

## Environment Variables

```env
# Gateway
GATEWAY_PORT=8000
GATEWAY_API_KEYS=key1,key2          # 쉼표 구분 API Keys
GATEWAY_JWT_SECRET=your-secret

# Internal services
LITELLM_URL=http://localhost:4000
OLLAMA_URL=http://localhost:11434

# External
SERPER_API_KEY=...
DOCS_API_URL=https://nodnjs-docs.koyeb.app/api
```

## docs 프로젝트 연결

기존 `docs_assistant.py`의 tool-call 루프를 Gateway 내 에이전트로 이관:

```
POST /v1/tasks
{
  "agent": "docs-assistant",
  "message": "문서 검색해줘: 테스트",
  "credentials": {"email": "...", "password": "..."}
}

→ Gateway가 LiteLLM에 chat completion 요청
→ tool_calls 감지 → httpx로 docs API 실행
→ 결과를 LLM에 피드백 → 최종 응답 반환
```

나중에 docs 프로젝트 자체도 로컬로 이관하면:
- `DOCS_API_URL=http://localhost:3000/api`로 변경만 하면 됨
