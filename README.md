# 🚀 Mac M4 Pro & Qwen3 기반 AutoGen 멀티 에이전트 개발 시스템

본 프로젝트는 **Mac M4 Pro (64GB RAM)** 환경에서 최신 **Qwen3 모델 시리즈**와 **AutoGen** 프레임워크를 결합하여, 기획부터 코드 구현, 검증까지 자율적으로 수행하는 **로컬 LLM 멀티 에이전트 개발 협업 시스템** 구축 가이드를 제공합니다.

---

## 🌟 시스템 핵심 가치

1.  **100% 로컬 보안**: 모든 데이터 처리가 로컬 기기 내에서 이루어져 민감한 소스코드 유출 위험이 없습니다.
2.  **TDD 자율 주행 (Strict TDD)**: 모든 설계와 구현은 테스트 주도 개발(Test-Driven Development) 방식을 따릅니다. **"No Test, No Code"** 원칙을 엄격히 준수합니다.
3.  **듀얼 맥 하이브리드 워크플로우**: 로컬 Qwen3(설계/검수)와 맥북 Claude Code(구현)의 협업을 통해 생산성을 극대화합니다.
4.  **프로젝트 헌법 (CLAUDE.md / RULES.md)**: 에이전트가 지켜야 할 규칙과 학습된 지식을 `CLAUDE.md`와 `RULES.md`에 집약하여 지속적으로 진화하는 개발 환경을 구축합니다.
5.  **최적화된 성능**: Qwen3 라인업(1.5b ~ 32b)을 전략적으로 배치하고 메모리 스왑을 최적화하여 64GB 환경에서 성능을 극대화합니다.
6.  **MCP 및 원격 연동**: Tailscale과 MCP(Model Context Protocol)를 통해 서로 다른 기기 간의 강력한 협업 환경을 제공합니다.

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
- [Git 관리 및 워크플로우 가이드](./docs/01_Setup/06_Git_관리_및_워크플로우_가이드.md)
- [Tailscale 기반 Ollama 원격 접속](./docs/01_Setup/07_Tailscale_기반_Ollama_원격_접속.md)
- [LiteLLM OpenAI 호환 프록시](./docs/01_Setup/08_LiteLLM_OpenAI_호환_프록시.md)
- [Anti-gravity 및 MCP 연동 가이드](./docs/01_Setup/09_Anti-gravity_및_MCP_연동_가이드.md)
- [Cursor + ngrok 로컬 Ollama 연동 가이드](./docs/01_Setup/10_Cursor_ngrok_로컬_Ollama_연동.md)
- [회사망 로컬 서버 노출 가이드](./docs/01_Setup/11_회사망_로컬_서버_노출_가이드.md)
- [Continue 로컬 LLM 최적화 설정](./docs/01_Setup/12_Continue_로컬_LLM_최적화_설정.md)
- [Aider 에이전트 설치 및 연동 가이드](./docs/01_Setup/13_Aider_에이전트_설치_및_연동_가이드.md)

### [02. 시스템 설계 (System Design)](./docs/02_System_Design)
- [Qwen3 모델 구성 전략](./docs/02_System_Design/01_Qwen3_모델_구성_전략.md)
- [LLM 라우터 구축 및 전략](./docs/02_System_Design/02_LLM_라우터_구축_및_전략.md)
- [메모리 관리 및 지연로딩 해결](./docs/02_System_Design/03_메모리_관리_및_지연로딩_해결.md)
- [컨텍스트 공유 및 최적화](./docs/02_System_Design/04_컨텍스트_공유_및_최적화.md)
- [맥미니 클러스터 확장 전략](./docs/02_System_Design/05_맥미니_클러스터_확장_전략.md)
- [Qwen3 토큰 사용량 및 효율성](./docs/02_System_Design/06_Qwen3_토큰_사용량_및_효율성.md)

### [03. 에이전트 시스템 (AutoGen Agents)](./docs/03_AutoGen_Agents)
- [에이전트 팀 구성 및 역할](./docs/03_AutoGen_Agents/01_에이전트_팀_구성_및_역할.md)
- [TDD 기반 협업 시스템 구현](./docs/03_AutoGen_Agents/02_TDD_기반_협업_시스템_구현.md)
- [개발자 협업 시스템 통합 코드](./docs/03_AutoGen_Agents/03_개발자_협업_시스템_통합_코드.md)
- [실전 TDD 워크플로우 및 자율 주행 루프](./docs/03_AutoGen_Agents/03_실전_TDD_워크플로우_및_자율_주행_루프.md)
- [RAG 및 문서 벡터화 가이드](./docs/03_AutoGen_Agents/04_RAG_및_문서_벡터화_가이드.md)
- [OpenWebUI RAG 및 지식 자산화](./docs/03_AutoGen_Agents/04-1_OpenWebUI_RAG_및_지식_자산화.md)
- [중계자 에이전트 라우팅 및 최종 정리](./docs/03_AutoGen_Agents/05_중계자_에이전트_라우팅_및_최종_정리.md)
- [중계자 난이도 판단 매뉴얼 및 Modelfile](./docs/03_AutoGen_Agents/05-1_중계자_난이도_판단_매뉴얼_및_Modelfile.md)
- [Local Executor 보안 및 샌드박스 설정](./docs/03_AutoGen_Agents/06_Local_Executor_보안_및_샌드박스_설정.md)
- [에이전트 전용 툴 및 인터페이스 설계](./docs/03_AutoGen_Agents/07_에이전트_전용_툴_및_인터페이스_설계.md)
- [실시간 에이전트 로그 모니터링](./docs/03_AutoGen_Agents/08_실시간_에이전트_로그_모니터링.md)
- [Qwen3 최적화 시스템 프롬프트](./docs/03_AutoGen_Agents/09_Qwen3_최적화_시스템_프롬프트.md)
- [최종 구축 체크리스트 및 마무리](./docs/03_AutoGen_Agents/10_최종_구축_체크리스트_및_마무리.md)
- [Ollama Modelfile 최적화 가이드](./docs/03_AutoGen_Agents/11_Ollama_Modelfile_최적화_가이드.md)
- [로컬 LLM 인터넷 연결 및 실시간 지식 확장](./docs/03_AutoGen_Agents/12_로컬_LLM_인터넷_연결_및_실시간_지식_확장.md)
- [LiteLLM Serper 안티그래비티 구축 가이드](./docs/03_AutoGen_Agents/13_LiteLLM_Serper_안티그래비티_구축_가이드.md)
- [프론티어 LLM 하이브리드 협업 가이드](./docs/03_AutoGen_Agents/13_프론티어_LLM_하이브리드_협업_가이드.md)
- [자기 성찰 및 성능 최적화 전략](./docs/03_AutoGen_Agents/14_자기_성찰_및_성능_최적화_전략.md)
- [간접 프롬프트 주입 방어 가이드](./docs/03_AutoGen_Agents/15_간접_프롬프트_주입_방어_가이드.md)
- [에이전트 컨트롤러 및 예외 처리 아키텍처](./docs/03_AutoGen_Agents/16_에이전트_컨트롤러_및_예외_처리_아키텍처.md)

### [04. 아키텍처 및 워크플로우 (Architecture)](./docs/04_Architecture)
- [듀얼 맥 & 3-Persona 워크플로우](./docs/04_Architecture/01_Dual_Mac_Git_Memory_Workflow.md)
- [Claude TDD 가이드라인 (Strict TDD)](./docs/04_Architecture/02_Claude_TDD_Guideline.md)
- [Claude Code 전문가 실전 팁](./docs/04_Architecture/03_Claude_Code_Expert_Tips.md)

### [05. 운영 및 유지보수 (Operations)](./docs/04_Operations)
- [GitHub 이슈 자동 처리 설정](./docs/04_Operations/01_GitHub_이슈_자동_처리_설정.md)
- [24시간 자동 운영 및 모니터링](./docs/04_Operations/02_24시간_자동_운영_및_모니터링.md)
- [매일의 실행 루틴 및 자동화](./docs/04_Operations/03_매일의_실행_루틴_및_자동화.md)

### [06. 트러블슈팅 (Troubleshooting)](./docs/05_Troubleshooting)
- [트러블슈팅 및 운영 팁](./docs/05_Troubleshooting/01_트러블슈팅_및_운영_팁.md)

### [99. 부록 (Appendix)](./docs/99_Appendix)
- [터미널 기본 가이드](./docs/99_Appendix/01_터미널_기본_가이드.md)
- [분산 추론 및 고급 네트워크 설정](./docs/99_Appendix/02_분산_추론_및_고급_네트워크_설정.md)

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
