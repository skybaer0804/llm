# 02. LLM 라우터 구축 및 전략

AutoGen 시스템의 핵심인 지능형 LLM 라우터(`router.py`)의 구현 원리와 작업 분배 전략을 다룹니다.

## 1. 라우터의 핵심 역할

라우터는 에이전트와 LLM 엔진(Ollama) 사이의 중재자 역할을 수행하며 다음 다섯 가지 핵심 기능을 담당합니다.

1.  **작업 분류 (Task Classification)**: 요청된 작업이 설계, 코딩, 검수 중 어디에 해당하는지 판단합니다.
2.  **보안 스캔 (Security Scan)**: 외부 데이터 내의 **간접 프롬프트 주입(Indirect Prompt Injection)** 위협을 탐지하는 입구 가이드레일 역할을 합니다.
3.  **모델 라우팅**: 작업 성격에 맞는 최적의 Qwen3 모델을 호출합니다.
4.  **메모리 오케스트레이션**: 모델 로드/언로드를 제어하여 64GB 메모리 임계치를 넘지 않도록 관리합니다.
5.  **헬스 모니터링**: Ollama 상태 및 추론 지연 시간(Latency)을 실시간으로 체크합니다.

## 2. 작업별 라우팅 규칙 (Routing Matrix)

라우터는 작업의 복잡도와 메모리 가용량을 고려하여 다음과 같이 모델을 배분합니다.

| 작업 범주 (Task Category) | 타겟 모델 (Ollama ID) | 메모리 점유 | 상주 전략 (Residency) | 주요 역할 및 적용 예시 |
| :--- | :--- | :--- | :--- | :--- |
| **Orchestration / Doc** | `qwen2.5:7b` | 약 4.7GB | **상시 상주** | 작업 분류(라우팅), 보안 스캔, 최종 문서화, 간단한 요약 |
| **Plan / Design** | `qwen3-coder-next:q4_K_M` | 약 52GB | **On-Demand** | 고수준 아키텍처 설계, 대규모 리팩토링 전략, 외부 프론티어 모델 연동 판단 |
| **Code / Implement** | `qwen3-coder:32b` | 약 19GB | **루프 상주** | 신규 기능 구현, 로직 수정, API 개발 (TDD 사이클 내 상주) |
| **Review / Test** | `qwen3-coder:14b` | 약 9GB | **루프 상주** | 유닛 테스트 생성, 보안 검수(Output Guardrail), 코드 리뷰 |

### 라우팅 판단 기준 (Decision Logic)
1.  **보안 우선**: 모든 입력은 `qwen2.5:7b` (Router)를 거쳐 간접 프롬프트 주입(Indirect Prompt Injection) 여부를 최우선으로 검사합니다.
2.  **난이도 기반**:
    *   **난이도 [상]**: 모듈 5개 이상의 의존성 재설계나 보안 아키텍처 설계가 필요한 경우 → **Architect** 호출 (메모리 스왑 발생).
    *   **난이도 [하]**: 단순 기능 구현, 단일 모듈 리팩토링, 버그 수정 → **Coder/Tester** 루프 내에서 처리.
3.  **경제적 운영**: 32B 모델이 2번 이상 해결하지 못한 과제에 대해서만 '상'으로 격상하여 52B 모델을 소환합니다.

## 3. 메모리 관리 로직 (Python pseudo-code)

라우터는 'TDD 루프 상주'와 '설계자 전전후 전환' 전략을 기반으로 메모리를 관리합니다.

```python
async def prepare_model(target_model):
    # 1. 아키텍트(52GB) 호출 시: 다른 모든 모델 언로드하여 가용 VRAM 확보
    if target_model == "qwen3-coder-next:q4_K_M":
        await unload_all_except(None)
        keep_alive = "0"  # 작업 종료 후 즉시 언로드
    
    # 2. 코더/테스터 호출 시: 아키텍트 모델이 메모리에 있다면 제거
    else:
        await unload_model("qwen3-coder-next:q4_K_M")
        keep_alive = "2h"  # 빠른 피드백 루프를 위해 2시간 상주 유지
    
    # 모델 로드 및 추론 수행 (Ollama API 호출)
    await ollama.generate(model=target_model, keep_alive=keep_alive, ...)
```

## 4. 라우터 연동 효과

- **리소스 최적화**: 사용하지 않는 모델을 즉시 언로드하여 시스템 지연(Swap 발생)을 방지합니다.
- **자동화된 워크플로우**: 에이전트가 모델 사양을 고민할 필요 없이 `task_type`만 지정하면 라우터가 최적의 자원을 할당합니다.
- **안정성**: 메모리 부족 시 요청을 대기시키거나 경고를 발생시켜 시스템 크래시를 예방합니다.
