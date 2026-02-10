# 02. TDD 기반 협업 시스템 구현

에이전트 팀이 단순한 코드 작성을 넘어, 테스트 주도 개발(Test Driven Development) 방식을 통해 고품질의 결과물을 산출하는 워크플로우를 다룹니다.

## 1. TDD 워크플로우 (Agentic TDD)

에이전트 시스템에서의 TDD는 다음과 같은 순서로 진행됩니다.

1.  **Test Case Design (Planner)**: 구현할 기능에 대한 유스케이스와 실패 조건(Edge Cases)을 포함한 테스트 시나리오를 정의합니다.
2.  **Test Implementation (Dev1 or Tester)**: 실제 기능 코드를 작성하기 전에 `pytest` 등을 활용한 테스트 코드를 먼저 작성합니다.
3.  **Initial Failure**: 작성된 테스트를 실행하여 실패함을 확인합니다.
4.  **Function Implementation (Dev1)**: 테스트를 통과하기 위한 최소한의 기능 코드를 작성합니다.
5.  **Test Pass & Refactor**: 테스트를 통과시킨 후, Dev2의 리뷰를 거쳐 코드를 최적화하고 다시 테스트를 돌려 회귀 오류가 없는지 확인합니다.

## 2. 에이전트별 TDD 프롬프트 전략

### Planner: 테스트 요구사항 정의
> "로그인 API를 설계할 때 다음 테스트 케이스를 반드시 포함해줘: 1. 올바른 계정 시 토큰 발급, 2. 잘못된 비밀번호 시 401 에러, 3. 존재하지 않는 계정 시 404 에러."

### Dev1: 테스트 우선 코딩
> "Planner가 정의한 시나리오에 맞춰 `tests/test_auth.py`를 먼저 작성하고, 이를 통과하는 `app/auth.py` 코드를 구현해."

### Tester: 자동 실행 및 디버그 루프
Tester 에이전트는 `UserProxyAgent`를 통해 실제 쉘 명령어를 실행합니다.
```bash
pytest tests/test_auth.py
```
- **성공 시**: "모든 테스트 통과. 검수자에게 전달합니다."
- **실패 시**: "테스트 실패 로그: [Error Details]. Dev1, 이 에러를 수정해줘."

## 3. Self-Debug 루프 (Self-Healing)

AutoGen의 `UserProxyAgent`와 `AssistantAgent` 간의 대화 루프를 활용하면 에러를 스스로 고치는 시스템을 만들 수 있습니다.

1.  코드 실행 중 에러 발생 (Traceback).
2.  Tester가 에러 메시지를 Dev1에게 전달.
3.  Dev1이 에러 원인을 분석하고 수정된 코드를 제시.
4.  Tester가 다시 실행하여 검증.

## 4. TDD 시스템의 장점

- **코드 품질 보장**: 로컬 LLM이 놓칠 수 있는 로직 오류를 실행 시점에 잡아낼 수 있습니다.
- **신뢰도 향상**: Human Lead의 개입 없이도 최소한의 작동 보증이 가능해집니다.
- **자동화 가속**: 테스트 통과 여부가 명확한 종료 조건(Termination Condition)이 되어 무한 루프를 방지합니다.
