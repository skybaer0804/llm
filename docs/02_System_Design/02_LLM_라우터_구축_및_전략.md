# 02. LLM 라우터 구축 및 전략 (Distributed Router)

AutoGen 시스템의 중추인 분산형 LLM 라우터(`router.py`)의 구현 원리와 맥북-맥미니 간의 분산 처리 전략을 다룹니다.

## 1. 분산형 라우터의 핵심 역할

라우터는 맥북(로컬)과 맥미니(원격)의 Ollama 인스턴스를 하나로 묶어 관리하며 다음 기능을 담당합니다.

1.  **지능형 작업 분류 (Local Analysis)**: 맥북의 `llama3.1:8b` 모델을 사용하여 요청의 난이도와 유형을 로컬에서 즉시 판단합니다.
2.  **보안 가드레일 (Input Guardrail)**: 외부 입력에 포함된 보안 위협을 로컬 게이트웨이 단계에서 선제적으로 차단합니다.
3.  **원격 워커 호출 (Remote Execution)**: 복잡한 작업은 썬더볼트 브리지를 통해 맥미니의 거대 모델(`qwen3-coder-next`)로 전송합니다.
4.  **분산 헬스 모니터링**: 맥북과 맥미니 두 기기의 Ollama 연결 상태와 메모리 상황을 실시간으로 체크합니다.

## 2. 분산 라우팅 구성 (Distributed Matrix)

| 기기 | 타겟 모델 | IP 주소 | 역할 | 비고 |
| :--- | :--- | :--- | :--- | :--- |
| **MacBook** | `llama3.1:8b` | `localhost` | **Gateway** | 난이도/보안 판단 (상시 상주) |
| **Mac Mini** | `qwen3-coder-next` | `169.254.19.104` | **Worker** | 실제 에이전트 작업 (2시간 상주) |

### 라우팅 판단 기준 (Decision Logic)
1.  **로컬 보안 검사**: 모든 입력은 맥북의 `llama3.1:8b`를 거쳐 보안 위협 여부를 검사합니다.
2.  **난이도 기반 위임**:
    *   **난이도 [상/중/하]**: 분석된 모든 유효한 작업은 맥미니의 고성능 모델로 위임하여 처리 품질을 극대화합니다.
    *   **보안 위협/단순 거절**: 맥북 단계에서 즉시 처리하여 맥미니의 자원 소모를 방지합니다.
3.  **썬더볼트 통신**: 169.254.x.x 대역의 썬더볼트 브리지 IP를 사용하여 내부망 통신 속도를 최대로 확보합니다.

## 3. 분산 헬스 체크 로직

라우터는 두 노드의 상태를 지속적으로 모니터링합니다.

```python
# router.py 헬스 체크 예시
@app.get("/health")
async def health_check():
    async with httpx.AsyncClient() as client:
        # 맥북 상태 확인
        mb_res = await client.get("http://localhost:11434")
        # 맥미니 상태 확인 (썬더볼트)
        mm_res = await client.get("http://169.254.19.104:11434")
    
    return {
        "nodes": {
            "macbook": "connected",
            "macmini": "connected"
        }
    }
```

## 4. 기대 효과

- **메모리 한계 극복**: 맥북의 24GB와 맥미니의 64GB를 합쳐 총 88GB의 통합 메모리를 활용하는 효과를 얻습니다.

## 5. 참고: 클라이언트 측 OpenAI 호환 (LiteLLM)

Antigravity, Continue 등 **OpenAI API 규격** 클라이언트가 맥미니의 Ollama를 그대로 쓰기 어렵다면, **LiteLLM**을 맥미니에 띄워 하나의 OpenAI 호환 엔드포인트로 제공할 수 있습니다. 멀티 모델 라우팅·Serper 검색 도구 연동 등은 [01_Setup 08. LiteLLM – OpenAI 호환 프록시](../01_Setup/08_LiteLLM_OpenAI_호환_프록시.md)를 참고하세요.
- **응답성 향상**: 가벼운 판단은 로컬에서 즉시 처리하고, 무거운 연산만 원격으로 보냄으로써 전체적인 워크플로우 속도가 개선됩니다.
- **안정성**: 한 기기의 메모리 부족이 다른 기기의 시스템 안정성에 영향을 주지 않는 격리된 환경을 제공합니다.
