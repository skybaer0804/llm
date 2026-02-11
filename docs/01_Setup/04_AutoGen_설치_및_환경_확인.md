# 04. AutoGen 설치 및 환경 확인

멀티 에이전트 협업을 위한 AutoGen 프레임워크를 설치하고 전체 시스템의 연결 상태를 최종 확인합니다.

## 1. AutoGen 및 필수 라이브러리 설치

반드시 가상환경(`.venv`)이 활성화된 상태에서 진행하세요.

```bash
# 가상환경 활성화 (필요 시)
source .venv/bin/activate

# AutoGen 핵심 라이브러리 설치
pip install pyautogen

# OpenAI 호환 라이브러리 (Ollama 연동용)
pip install openai

# 설치 확인
python3 -c "import autogen; print(f'AutoGen 버전: {autogen.__version__}')"
python3 -c "import openai; print('OpenAI 라이브러리 준비 완료')"
```

## 2. 핵심 에이전트 개념 이해

AutoGen은 크게 두 가지 타입의 에이전트를 사용합니다.

- **AssistantAgent (역할 수행자)**: LLM을 기반으로 특정 임무(설계, 코딩, 리뷰)를 수행합니다. 시스템 메시지를 통해 정체성을 부여합니다.
- **UserProxyAgent (사용자 대리인)**: 사용자를 대신하여 다른 에이전트와 대화하거나 코드를 실행합니다. 사람이 개입해야 할 때 중간에서 중재하는 역할도 수행합니다.

## 3. Ollama 연동 설정 팁

AutoGen에서 로컬 Ollama 모델을 호출할 때 다음과 같은 설정(`config_list`)을 주로 사용합니다.

```python
config_list = [
    {
        "model": "qwen3-coder:30b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama", # 로컬이므로 임의의 값 입력
    }
]
```

## 4. 전체 시스템 연결 최종 확인

모든 구성 요소가 준비되었는지 터미널에서 순차적으로 확인합니다.

```bash
# 1. Ollama API 정상 작동 확인
curl http://localhost:11434

# 2. 필수 모델 존재 여부 확인
ollama list
# qwen3-coder-next:q4_K_M, qwen3-coder:30b, qwen3:14b가 목록에 있어야 함

# 3. 모델 응답 테스트 (Architect 모델 예시)
ollama run qwen3-coder-next:q4_K_M "현재 시스템 준비 상태를 점검해줘."
# Ctrl+D로 종료
```

모든 테스트가 통과되었다면 이제 시스템 설계 단계로 넘어갈 준비가 완료된 것입니다. 추가로, 터미널 기반의 코드 분석 및 수정을 위해 [Claude Code CLI](./05_Claude_Code_CLI_설치_및_설정.md)를 설정하면 더욱 효율적인 개발 환경을 구축할 수 있습니다.
