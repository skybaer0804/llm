# Agent Instructions & Project Rules

이 파일은 안티그래비티(Anti-gravity) 및 기타 AI 에이전트가 프로젝트를 이해하고 행동하는 방침을 정의합니다.

## 1. 기본 원칙
- **언어**: 모든 답변과 기술 문서는 한국어로 작성하는 것을 원칙으로 합니다.
- **실시간 정보**: 실시간 정보가 필요할 경우 반드시 `search` 도구(LiteLLM/Serper 연동)를 사용합니다.
- **코드 스타일**: 가급적 원본 코드의 컨벤션을 유지하며, 변경 사항에 대해 상세히 설명합니다.

## 2. 하드웨어 및 인프라 환경
- **Main Server**: 맥미니 M4 64GB (AI 엔진, Ollama, LiteLLM 구동)
- **Client**: 맥북 (안티그래비티 IDE, 실제 작업 공간)
- **Network**: Tailscale을 통한 보안 및 원격 연결 (Base URL: `http://[MacMini-IP]:4000/v1`)

## 3. 에이전트 행동 지침
- 실내외 상황에 맞춰 최적의 모델(local-search-model 등)을 선택하여 활용합니다.
- 복잡한 개발 작업 시 MCP(Model Context Protocol) 서버를 적극 활용하여 맥미니의 기능을 도구로 사용합니다.
- 프로젝트 루트의 `docs/` 폴더 내에 기술된 가이드라인(Setup, Architecture, Operations 등)을 준수합니다.

---

*이 설정은 프로젝트의 효율적인 원격 개발과 로컬 LLM 자원의 극대화를 위해 작성되었습니다.*
