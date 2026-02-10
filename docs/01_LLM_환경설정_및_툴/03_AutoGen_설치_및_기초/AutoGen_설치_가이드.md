## 2. AutoGen 설치 (Python 환경)
AutoGen은 Python 라이브러리이므로 가상 환경에 설치하는 것이 안전합니다. 맥미니는 기본적으로 Python 3가 설치되어 있습니다. 
가상 환경 생성 및 활성화:
bash
python3 -m venv autogen-env
source autogen-env/bin/activate
코드를 사용할 때는 주의가 필요합니다.

AutoGen 라이브러리 설치: 공식 Microsoft AutoGen 가이드에 따라 아래 패키지를 설치합니다.
bash
pip install pyautogen
코드를 사용할 때는 주의가 필요합니다.

AutoGen Studio (UI 버전) 설치 (선택 사항): 웹 화면에서 에이전트를 관리하고 싶다면 설치하세요.
bash
pip install autogenstudio
autogenstudio ui --port 8081
코드를 사용할 때는 주의가 필요합니다.

설치 후 브라우저에서 http://localhost:8081로 접속하면 됩니다. 
팁: Ollama와 AutoGen 연결하기 
AutoGen에서 로컬 Ollama를 사용하려면 OAI_CONFIG_LIST 설정 시 base_url을 http://localhost:11434/v1로, api_type을 ollama로 지정해야 합니다. 

해당 환경에 openai 라이브러리가 설치
pip install openai

설치확인
python3 -c "import openai; print('설치 완료')"