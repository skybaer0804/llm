## AutoGen: 멀티 에이전트 프레임워크

### AutoGen이란?

Microsoft의 오픈소스 프레임워크로, **여러 AI 에이전트가 협력해서 복잡한 작업을 자동화**합니다.

```
일반인 설명: ChatGPT 여러 개가 팀처럼 회의하면서 문제 해결
```

### 핵심 개념

#### AssistantAgent (AI 역할자)
```python
from autogen import AssistantAgent

assistant = AssistantAgent(
    "Dev1",
    system_message="너는 시니어 개발자야. 코드 작성하고 테스트 커버리지 체크.",
    llm_config={"config_list": config}
)
```

#### UserProxyAgent (인간 플레이어)
```python
from autogen import UserProxyAgent

human = UserProxyAgent(
    "Human",
    human_input_mode="ALWAYS",  # 중요 결정 시 당신에게 물어보기
    code_execution_config={"work_dir": "./repo"}
)
```

### 설치

```bash
pip install pyautogen
```