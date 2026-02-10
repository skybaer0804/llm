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

AutoGen의 `UserProxyAgent`와 `AssistantAgent` 간의 대화 루프를 활용하면 에러를 스스로 고치는 시스템을 만들 수 있습니다. 이때 **Router(중계자) 에이전트**를 배치하면 에러 로그를 분석하여 단순 오타 수정인지 아키텍처 재설계인지를 지능적으로 판단하여 루프 효율을 높일 수 있습니다. (자세한 내용은 [05. 중계자 에이전트 라우팅](./05_중계자_에이전트_라우팅_및_최종_정리.md) 참조)

1.  코드 실행 중 에러 발생 (Traceback).
2.  **Router**가 에러 메시지를 분석.
3.  단순 오류 시 Dev1(Coder)에게 전달, 구조적 결함 시 Architect에게 전달.
4.  담당 에이전트가 에러를 수정하고 Tester가 다시 검증.

## 4. TDD 시스템의 장점

- **코드 품질 보장**: 로컬 LLM이 놓칠 수 있는 로직 오류를 실행 시점에 잡아낼 수 있습니다.
- **신뢰도 향상**: Human Lead의 개입 없이도 최소한의 작동 보증이 가능해집니다.
- **자동화 가속**: 테스트 통과 여부가 명확한 종료 조건(Termination Condition)이 되어 무한 루프를 방지합니다.

---

## 5. 실전 구현: Local Executor (코드 실행기)

LLM은 코드를 작성할 뿐 직접 실행할 수 없습니다. 따라서 실제 환경에서 테스트를 수행할 수 있는 실행기 연결이 필수적입니다.

### Python 기반 Executor 구현 예시
`subprocess` 모듈을 사용하여 에이전트가 짠 코드를 실행하고 결과를 다시 피드백합니다. 보안을 위해 반드시 샌드박스 환경을 구축해야 합니다. (자세한 내용은 [06. Local Executor 보안 및 샌드박스 설정](./06_Local_Executor_보안_및_샌드박스_설정.md) 참조)

```python
import subprocess

def execute_test(code, test_script):
    # 1. 에이전트가 작성한 코드를 임시 파일로 저장
    with open("temp_code.py", "w") as f:
        f.write(code)
    with open("temp_test.py", "w") as f:
        f.write(test_script)
    
    # 2. pytest 등을 이용해 실행
    result = subprocess.run(["python3", "temp_test.py"], capture_output=True, text=True)
    
    # 3. 결과 리턴 (에러 발생 시 stderr 포함)
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
```

---

## 6. 에이전트 간 대화 프로토콜 (JSON 규격)

에이전트끼리 주고받는 데이터를 JSON으로 규격화하면 파싱 오류를 줄이고 자동화 루프를 견고하게 만들 수 있습니다.

### 프로토콜 사용의 장점
1.  **파싱 최적화**: "네, 알겠습니다" 같은 불필요한 서술어를 제거하고 필요한 정보만 추출합니다.
2.  **데이터 누락 방지**: 필수 항목(파일 경로, 에러 위치 등)을 강제합니다.
3.  **자동화 호환성**: Local Executor가 JSON 데이터를 즉시 해석하여 실행에 활용할 수 있습니다.

### JSON 설계 예시
```json
{
  "sender": "Reviewer",
  "recipient": "Coder",
  "status": "FAIL",
  "task_id": "auth_feature_01",
  "feedback": {
    "error_type": "AssertionError",
    "location": "test_auth.py:line 24",
    "message": "Expected status 200 but got 401",
    "suggestion": "토큰 검증 로직에서 만료된 토큰 처리 부분을 확인해줘."
  },
  "code_context": "..." 
}
```

### 좋은 설계의 핵심
가장 좋은 설계는 **"피드백 루프의 명확성"**입니다. 에이전트 A의 Output이 에이전트 B의 Input이 될 때, 다음 단계에서 무엇을 해야 할지(Action)가 명확하게 정의되어야 합니다.
