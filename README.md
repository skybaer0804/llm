# 🚀 Mac M4 Pro & Qwen3 기반 AutoGen 멀티 에이전트 개발 시스템

본 프로젝트는 **Mac M4 Pro (64GB RAM)** 환경에서 최신 **Qwen3 모델 시리즈**와 **AutoGen** 프레임워크를 결합하여, 기획부터 코드 구현, 검증까지 자율적으로 수행하는 **로컬 LLM 멀티 에이전트 개발 협업 시스템** 구축 가이드를 제공합니다.

---

## 🌟 시스템 핵심 가치

1.  **100% 로컬 보안**: 모든 데이터 처리가 로컬 기기 내에서 이루어져 민감한 소스코드 유출 위험이 없습니다.
2.  **TDD 자율 주행 (Strict TDD)**: 모든 설계와 구현은 테스트 주도 개발(Test-Driven Development) 방식을 따릅니다. **"No Test, No Code"** 원칙을 엄격히 준수합니다.
3.  **듀얼 맥 하이브리드 워크플로우**: 로컬 Qwen3(설계/검수)와 맥북 Claude Code(구현)의 협업을 통해 생산성을 극대화합니다.
4.  **프로젝트 헌법 (CLAUDE.md)**: 에이전트가 지켜야 할 규칙과 학습된 지식을 `CLAUDE.md`에 집약하여 지속적으로 진화하는 개발 환경을 구축합니다.
5.  **최적화된 성능**: Qwen3 라인업(1.5b ~ 32b)을 전략적으로 배치하고 메모리 스왑을 최적화하여 64GB 환경에서 성능을 극대화합니다.

---

## 🤖 에이전트 팀 구성 (The Agency)

프로젝트 규모와 목적에 따라 두 가지 운영 모드를 지원합니다.

### Mode A: Dual Mac 하이브리드 (Qwen3 + Claude Code)
- **설계/검수**: 로컬 Mac M4 Pro (Qwen3)
- **구현**: 맥북 (Claude Code)
- **특징**: 프론티어 LLM의 강력한 코딩 능력과 로컬 LLM의 보안/설계 능력을 결합.

### Mode B: 100% 로컬 AutoGen (Full Local)
- **모든 역할**: 로컬 Mac M4 Pro (Qwen3 시리즈)
- **특징**: 완전한 오프라인 환경, API 비용 제로, 고도의 자동화 루프.

---

## 📈 개발 생산성 기대 효과

로컬 에이전시 도입 시 수동 개발 대비 다음과 같은 생산성 향상을 목표로 합니다.

- **보일러플레이트 작성**: 1시간 → 2분 (**2,000%↑**)
- **TDD 기반 개발**: 2시간 → 10분 (**1,200%↑**)
- **디버깅 및 문서화**: 기존 대비 **6~10배** 빠른 처리 속도
- **종합 생산성**: 숙련된 사수 1명이 주니어 개발자 3명을 지휘하는 수준의 퍼포먼스

---

## 📂 프로젝트 구조 및 문서 가이드

### [00. 시작하기 (Intro)](./docs/00_Intro)
- [로컬 LLM 개요 및 구축 목적](./docs/00_Intro/01_로컬_LLM_개요.md)
- [시스템 사양 및 요구사항](./docs/00_Intro/02_시스템_사양_및_요구사항.md)
- [개발 생산성 및 기대 효과](./docs/00_Intro/03_개발_생산성_및_기대_효과.md)

### [01. 환경 설정 (Setup)](./docs/01_Setup)
- [macOS 시스템 최적화](./docs/01_Setup/00_macOS_시스템_최적화.md)
- [Python 및 가상환경 설정](./docs/01_Setup/01_Python_및_가상환경_설정.md)
- [Docker 및 보안 설정](./docs/01_Setup/02_Docker_및_보안_설정.md)
- [Ollama 설치 및 웹 UI 구성](./docs/01_Setup/03_Ollama_설치_및_웹UI_구성.md)
- [AutoGen 설치 및 환경 확인](./docs/01_Setup/04_AutoGen_설치_및_환경_확인.md)
- [Claude Code CLI 설치 및 설정](./docs/01_Setup/05_Claude_Code_CLI_설치_및_설정.md)

### [02. 시스템 설계 (System Design)](./docs/02_System_Design)
- [Qwen3 모델 구성 전략](./docs/02_System_Design/01_Qwen3_모델_구성_전략.md)
- [LLM 라우터 구축 및 전략](./docs/02_System_Design/02_LLM_라우터_구축_및_전략.md)
- [메모리 관리 및 지연로딩 해결](./docs/02_System_Design/03_메모리_관리_및_지연로딩_해결.md)
- [컨텍스트 공유 및 최적화](./docs/02_System_Design/04_컨텍스트_공유_및_최적화.md)

### [03. 에이전트 시스템 (AutoGen Agents)](./docs/03_AutoGen_Agents)
- [에이전트 팀 구성 및 역할](./docs/03_AutoGen_Agents/01_에이전트_팀_구성_및_역할.md)
- [TDD 기반 협업 시스템 구현](./docs/03_AutoGen_Agents/02_TDD_기반_협업_시스템_구현.md)
- [실전 TDD 워크플로우 및 자율 주행 루프](./docs/03_AutoGen_Agents/03_실전_TDD_워크플로우_및_자율_주행_루프.md)
- [RAG 및 문서 벡터화 가이드](./docs/03_AutoGen_Agents/04_RAG_및_문서_벡터화_가이드.md)
- [로컬 LLM 인터넷 연결 및 지식 확장](./docs/03_AutoGen_Agents/12_로컬_LLM_인터넷_연결_및_실시간_지식_확장.md)
- *... 그 외 에이전트 로그 모니터링, 샌드박스 설정 등 포함*

### [04. 아키텍처 및 워크플로우 (Architecture)](./docs/04_Architecture)
- [듀얼 맥 & 3-Persona 워크플로우](./docs/04_Architecture/01_Dual_Mac_Git_Memory_Workflow.md)
- [Claude TDD 가이드라인 (Strict TDD)](./docs/04_Architecture/02_Claude_TDD_Guideline.md)
- [Claude Code 전문가 실전 팁](./docs/04_Architecture/03_Claude_Code_Expert_Tips.md)

### [05. 운영 및 트러블슈팅](./docs/04_Operations)
- [GitHub 이슈 자동 처리 설정](./docs/04_Operations/01_GitHub_이슈_자동_처리_설정.md)
- [24시간 자동 운영 및 모니터링](./docs/04_Operations/02_24시간_자동_운영_및_모니터링.md)
- [트러블슈팅 및 운영 팁](./docs/05_Troubleshooting/01_트러블슈팅_및_운영_팁.md)

---

## 🛠 빠른 시작 (Quick Start)

1.  **환경 준비**
    ```bash
    # 가상환경 생성 및 활성화
    python3 -m venv .venv
    source .venv/bin/activate

    # 필수 패키지 설치
    pip install "pyautogen[lmm]" docker
    ```

2.  **Ollama 모델 준비**
    ```bash
    # 주요 모델 다운로드
    ollama run qwen3:32b-coder
    ollama run qwen3:14b-coder
    ollama run qwen3:1.5b
    ```

3.  **실행**
    `docs/03_AutoGen_Agents/03_개발자_협업_시스템_통합_코드.md`를 참고하여 메인 스크립트를 구성하고 실행하십시오.

---

## 🤝 기여 및 라이선스
본 프로젝트는 교육 및 연구 목적으로 제작되었으며, 누구나 자유롭게 수정 및 배포할 수 있습니다.
