# Mac M4 Pro Qwen3 AutoGen 멀티 에이전트 시스템 구축 가이드

본 프로젝트는 Mac M4 Pro 64GB 환경에서 최신 Qwen3 모델 시리즈를 활용하여 AutoGen 기반의 지능형 멀티 에이전트 협업 시스템을 구축하고 운영하는 종합 가이드를 제공합니다.

## 📂 문서 목차

### [00. 시작하기 (Intro)](./docs/00_Intro)
*   [01. 로컬 LLM 개요 및 구축 목적](./docs/00_Intro/01_로컬_LLM_개요.md)
*   [02. 시스템 사양 및 요구사항](./docs/00_Intro/02_시스템_사양_및_요구사항.md)
*   [03. 개발 생산성 및 기대 효과](./docs/00_Intro/03_개발_생산성_및_기대_효과.md)

### [01. 환경 설정 (Setup)](./docs/01_Setup)
*   [01. Python 및 가상환경 설정](./docs/01_Setup/01_Python_및_가상환경_설정.md)
*   [02. Docker 및 보안 설정](./docs/01_Setup/02_Docker_및_보안_설정.md)
*   [03. Ollama 설치 및 웹 UI 구성](./docs/01_Setup/03_Ollama_설치_및_웹UI_구성.md)
*   [04. AutoGen 설치 및 환경 확인](./docs/01_Setup/04_AutoGen_설치_및_환경_확인.md)

### [02. 시스템 설계 (System Design)](./docs/02_System_Design)
*   [01. Qwen3 모델 구성 전략](./docs/02_System_Design/01_Qwen3_모델_구성_전략.md)
*   [02. LLM 라우터 구축 및 전략](./docs/02_System_Design/02_LLM_라우터_구축_및_전략.md)
*   [03. 메모리 관리 및 지연로딩 해결](./docs/02_System_Design/03_메모리_관리_및_지연로딩_해결.md)
*   [04. 컨텍스트 공유 및 최적화](./docs/02_System_Design/04_컨텍스트_공유_및_최적화.md)

### [03. 에이전트 시스템 (AutoGen Agents)](./docs/03_AutoGen_Agents)
*   [01. 에이전트 팀 구성 및 역할](./docs/03_AutoGen_Agents/01_에이전트_팀_구성_및_역할.md)
*   [02. TDD 기반 협업 시스템 구현](./docs/03_AutoGen_Agents/02_TDD_기반_협업_시스템_구현.md)
*   [03. 실전 TDD 워크플로우 및 자율 주행 루프](./docs/03_AutoGen_Agents/03_실전_TDD_워크플로우_및_자율_주행_루프.md)
*   [04. RAG 및 문서 벡터화 가이드](./docs/03_AutoGen_Agents/04_RAG_및_문서_벡터화_가이드.md)
*   [05. 중계자 에이전트 라우팅 및 최종 정리](./docs/03_AutoGen_Agents/05_중계자_에이전트_라우팅_및_최종_정리.md)
*   [06. Local Executor 보안 및 샌드박스 설정](./docs/03_AutoGen_Agents/06_Local_Executor_보안_및_샌드박스_설정.md)
*   [07. 에이전트 전용 툴 및 인터페이스 설계](./docs/03_AutoGen_Agents/07_에이전트_전용_툴_및_인터페이스_설계.md)
*   [08. 실시간 에이전트 로그 모니터링](./docs/03_AutoGen_Agents/08_실시간_에이전트_로그_모니터링.md)
*   [09. Qwen3 최적화 시스템 프롬프트](./docs/03_AutoGen_Agents/09_Qwen3_최적화_시스템_프롬프트.md)
*   [10. 최종 구축 체크리스트 및 마무리](./docs/03_AutoGen_Agents/10_최종_구축_체크리스트_및_마무리.md)
*   [11. Ollama Modelfile 최적화 가이드](./docs/03_AutoGen_Agents/11_Ollama_Modelfile_최적화_가이드.md)

### [04. 운영 및 자동화 (Operations)](./docs/04_Operations)
*   [01. GitHub 이슈 자동 처리 설정](./docs/04_Operations/01_GitHub_이슈_자동_처리_설정.md)
*   [02. 24시간 자동 운영 및 모니터링](./docs/04_Operations/02_24시간_자동_운영_및_모니터링.md)

### [05. 트러블슈팅 (Troubleshooting)](./docs/05_Troubleshooting)
*   [01. 트러블슈팅 및 운영 팁](./docs/05_Troubleshooting/01_트러블슈팅_및_운영_팁.md)

### [99. 부록 (Appendix)](./docs/99_Appendix)
*   [01. 터미널 기본 가이드](./docs/99_Appendix/01_터미널_기본_가이드.md)
*   [02. 분산 추론 및 고급 네트워크 설정](./docs/99_Appendix/02_분산_추론_및_고급_네트워크_설정.md)

---

## 🚀 주요 특징
- **Qwen3 기반 최적화**: Architect(Coder-Next), Coder(32b), Reviewer/Tester(14b)의 완벽한 역할 분담.
- **하이브리드 프롬프트 전략**: Ollama Modelfile을 활용한 페르소나 고정과 API를 통한 동적 지시 결합.
- **지능형 라우팅**: 1.5b 초경량 모델을 활용한 상황 판단 및 64GB 메모리 효율 극대화(자동 스왑).
- **TDD 자율 주행**: 에이전트 스스로 테스트를 설계, 작성, 실행하고 에러를 분석하여 코드를 수정하는 루프 구현.
- **문서화 자동화**: 협업의 모든 과정을 추적하여 배포 가능한 수준의 기술 문서를 자동으로 생성.
