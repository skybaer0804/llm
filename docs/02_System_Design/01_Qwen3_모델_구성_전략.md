# 01. 분산형 모델 구성 전략 (Distributed Multi-Model System)

본 시스템은 맥북(24GB)과 맥미니(64GB)를 연동하여, 각 기기의 메모리 사양에 최적화된 모델을 분산 배치하는 전략을 사용합니다. 에이전트 팀 구성 및 역할 문서의 페르소나와 모델 매핑을 기준으로 합니다.

## 1. 분산 모델 배치 전략

### 1.1 기기별 요약

| 기기 | 상주/주요 모델 | 역할 | 핵심 임무 |
| :--- | :--- | :--- | :--- |
| **💻 MacBook (24GB)** | `qwen2.5:7b` | **지능형 Gateway (Router)** | 작업 분류(난이도 판단), 1차 보안 검문소(Input Guardrail), 에이전트 라우팅, Documenter |
| **🖥️ Mac Mini (64GB)** | `qwen3-coder-next:q4_K_M` | **Worker 군단** | Planner(Architect), Dev1(Coder), Dev2(Reviewer), Tester 등 고성능 연산 |

### 1.2 에이전트별 모델 매핑 (참조: 에이전트 팀 구성 및 역할)

| 에이전트 | 모델 | 배치 | 비고 |
| :--- | :--- | :--- | :--- |
| **Router** | `qwen2.5:7b` | MacBook | 항시 상주, 반응 속도 최적화 |
| **Planner (Architect)** | `qwen3-coder-next:q4_K_M` (~52GB) | Mac Mini | 작업 시에만 로드, 완료 후 메모리 반납 |
| **Dev1_Senior (Coder)** | `qwen3-coder-next:q4_K_M` | Mac Mini | Planner와 동일 모델, 호출 시점/페르소나로 구분 |
| **Dev2_Reviewer** | `qwen3-coder-next:q4_K_M` | Mac Mini | Tester와 모델 공유, 페르소나 전환 |
| **Tester_QA** | `qwen3-coder-next:q4_K_M` | Mac Mini | Reviewer와 모델 공유 |
| **Documenter** | `qwen2.5:7b` | MacBook (또는 상주 모델) | 최종 보고서·기술 문서 |
| **Frontier LLM** | GPT-4o, Claude 3.5 Sonnet 등 | 외부(클라우드) | 로컬 한계 시 선택적 SOS 호출 |

## 2. 페르소나 운영 메커니즘

모든 고부하 페르소나(Planner, Coder, Reviewer, Tester)는 맥미니의 대형 모델이 담당하며, 맥북의 Gateway(Router) 모델이 라우팅·보안·문서화를 담당합니다.

1.  **Stateless Switching**: 페르소나 전환 시 이전 대화 기록을 초기화하고, 필요한 컨텍스트만 맥미니 Worker로 전달합니다. Reviewer와 Tester는 동일 `qwen3-coder-next`에서 호출 시점에만 페르소나를 전환합니다.
2.  **TDD-Driven Implementation**: Planner가 테스트 시나리오를 정의하고, Coder와 Reviewer가 상주하며 TDD 사이클을 반복합니다. 난이도 중/상일 경우 Reviewer의 '자기 성찰 루프'로 품질을 강화합니다.
3.  **Thunderbolt Bridge Networking**: 맥북과 맥미니 간 통신은 썬더볼트 브리지(10Gbps+)로 이루어지며, 원격 호출 오버헤드를 최소화합니다.
4.  **Memory Management**: 맥북은 `qwen2.5:7b`를 상시 상주시켜 빠른 응답을 유지하고, 맥미니는 Architect는 필요 시 로드·반납, Coder/Reviewer·Tester용 모델은 64GB 범위 내에서 상주·공유로 운용합니다.
5.  **Frontier LLM 연동**: Planner 등 로컬 모델의 지능 한계(최신 라이브러리, 복잡한 아키텍처) 발생 시 Frontier LLM 호출용 프롬프트를 생성해 선택적 SOS 연동을 합니다.

## 3. 워크플로우 루프

*   **Gateway (MacBook)**: 요청 수령 → 난이도·자기성찰 여부 판단 → 보안 검사(Input Guardrail) → Worker 위임 → (완료 후) Documenter로 최종 보고서 생성.
*   **Worker (Mac Mini)**: Planner 설계 → Coder 구현 ↔ Reviewer 검수(상주 루프) → Tester 검증 → 결과 반환.
*   **Git (Shared)**: 두 기기 간 결과물은 Git 레포지토리로 동기화 및 관리.
*   **Human_Lead**: Router 판단 불가 시 개입, 최종 코드·배포 승인.
