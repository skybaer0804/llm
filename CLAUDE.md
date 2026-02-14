# CLAUDE.md - Project Constitution & Learned Skills

이 파일은 프로젝트의 모든 에이전트(Claude, Ollama 등)가 준수해야 할 핵심 규칙과 학습된 지식을 담고 있습니다.

## 🛠 Project Context
- **Architecture**: Distributed Dual-Mac (MacBook Gateway + Mac Mini Worker)
- **Core Models**: 
  - Gateway: `llama3.1:8b` (MacBook, 24GB)
  - Worker: `qwen3-coder-next` (Mac Mini, 64GB)
  - Cloud: Gemini 3 Flash
- **Environment**: macOS (M4 Pro), Python 3.12, venv (.venv)
- **Networking**: Thunderbolt Bridge (169.254.x.x)
- **Optimization**: `gpu_config.py`를 통한 Apple Silicon GPU 가속 활성화 필수.

## 🤖 Global Rules (ALL Agents)
- **Rule 1 (Continuous Learning)**: 모든 세션 종료 전, 새로운 해결책이나 최적화 기법을 찾았다면 이 파일의 `Learned Skills` 섹션에 업데이트할 것.
- **Rule 2 (Plan First)**: 복잡한 로직 수정 시 반드시 `Plan Mode`로 진입하여 전체 구조를 먼저 승인받을 것.
- **Rule 3 (Distributed Awareness)**: 모든 원격 호출은 썬더볼트 브리지 IP를 사용하며, 맥미니의 Ollama 상태를 항상 체크할 것.
- **Rule 4 (No Redundancy)**: `requirements.txt`에 패키지 추가 시 기존 패키지와 충돌 여부를 먼저 체크할 것.
- **Rule 5 (TDD-First)**: 코드를 작성하기 전에 항상 테스트 코드를 먼저 작성하거나 Architect의 테스트 시나리오를 검증할 것.

## 🏠 Local Model Specifics (Distributed)
- **Gateway (MacBook)**: 작업 분류, 보안 스캔, 라우팅 전담.
- **Worker (Mac Mini)**: 설계, 구현, 검수 등 고성능 연산 전담.
- 로컬 모델이 수정한 코드는 반드시 `git diff`를 통해 변경 사항을 자가 검토한다.
- 성능 한계가 감지되면 즉시 `EXTERNAL_CONSULT`를 선언하여 상위 모델(Claude/Gemini)에게 지원을 요청한다.

## 💡 Learned Skills & Prompts (Updated: 2026-02-12)
- **Distributed Setup**: 맥미니 Ollama 접속을 위해 `OLLAMA_HOST="0.0.0.0"` 설정 필수.
- **Error Fix (ResolutionImpossible)**: `requirements.txt`의 버전 고정을 풀고 `pip install --upgrade pip` 선행 후 재시도.
- **Optimization (GPU Acceleration)**: Metal API 호출 시 컨텍스트 윈도우 크기에 따른 레이어 할당량 최적화가 성능의 핵심임.
- **Sub-agent usage**: 복잡한 라우팅 로직은 `use subagents` 지시어를 활용해 분산 처리하여 메인 컨텍스트를 보호함.

---
*참고: 이 파일은 에이전트에 의해 지속적으로 업데이트됩니다.*
