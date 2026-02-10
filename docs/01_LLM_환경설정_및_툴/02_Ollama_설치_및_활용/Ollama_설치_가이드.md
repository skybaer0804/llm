## 1. Ollama 설치 및 실행 (터미널)
터미널을 열고 아래 명령어를 순서대로 입력하세요.
Homebrew 설치 (이미 설치되어 있다면 건너뛰세요):
bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
코드를 사용할 때는 주의가 필요합니다.

Ollama 설치: Homebrew Formulae를 이용해 설치합니다.
bash
brew install ollama
코드를 사용할 때는 주의가 필요합니다.

Ollama 서비스 시작:
bash
brew services start ollama
코드를 사용할 때는 주의가 필요합니다.

모델 다운로드 및 실행: 테스트로 llama3 모델을 실행해 보세요.
bash
ollama run llama3
코드를 사용할 때는 주의가 필요합니다.