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

| 작업 범주 (Task Category) | 타겟 모델 | 적용 예시 |
| :--- | :--- | :--- |
| **Plan / Design** | `qwen3-coder-next:q4_K_M` | 아키텍처 설계, 요구사항 정의서 작성, 마일스톤 설정 |
| **Code / Implement** | `qwen3-coder:32b` | 신규 기능 개발, 리팩터링, API 구현 |
| **Review / Test** | `qwen3:14b` | PR 리뷰, 유닛 테스트 작성, 정적 분석 |

## 3. 메모리 관리 로직 (Python pseudo-code)

라우터는 다음과 같은 로직으로 메모리를 관리합니다.

```python
async def prepare_model(target_model):
    if target_model == "qwen3-coder-next:q4_K_M":
        # 설계자 호출 시: 다른 모든 모델 언로드 (52GB 확보)
        await unload_all_except(None)
    else:
        # 개발자/검수자 호출 시: 설계자 모델이 있다면 언로드
        await unload_model("qwen3-coder-next:q4_K_M")
    
    # 모델 로드 대기 및 추론 시작
    await ollama.load(target_model)
```

## 4. 라우터 연동 효과

- **리소스 최적화**: 사용하지 않는 모델을 즉시 언로드하여 시스템 지연(Swap 발생)을 방지합니다.
- **자동화된 워크플로우**: 에이전트가 모델 사양을 고민할 필요 없이 `task_type`만 지정하면 라우터가 최적의 자원을 할당합니다.
- **안정성**: 메모리 부족 시 요청을 대기시키거나 경고를 발생시켜 시스템 크래시를 예방합니다.
