# 05. Claude Code CLI 설치 및 설정

Anthropic에서 제공하는 Claude Code CLI를 설치하여 터미널 환경에서 직접 코드를 분석하고 수정할 수 있는 환경을 구축합니다. Claude Code는 실제 파일 시스템에 접근하여 코드를 수정할 수 있는 강력한 도구입니다.

## 1. 사전 준비 (Node.js 확인)

Claude Code는 Node.js 환경에서 동작합니다. 시스템에 Node.js(버전 18 이상)가 설치되어 있는지 확인합니다.

```bash
# Node.js 버전 확인
node -v
```

버전 숫자가 나오지 않거나 18 미만인 경우, [Node.js 공식 사이트](https://nodejs.org/)에서 LTS 버전을 설치하십시오.

## 2. 사전 준비 (Git 설치 및 설정)

Git은 Claude Code CLI의 '눈'과 '기억' 역할을 하기 때문에 반드시 설치되어 있어야 합니다. Claude Code는 단순히 코드를 짜주는 것을 넘어, Git 히스토리를 보고 "아, 이전에 여기까지 작업했구나"를 파악하거나, 작업이 잘못되었을 때 이전으로 되돌리는 작업을 수행합니다.

### 왜 Claude Code에 Git이 필요한가요?

*   **진행 상황 파악**: `git log`와 `git diff`를 통해 클로드가 "작업이 어디서 멈췄는지"를 스스로 읽어냅니다.
*   **안전 장치**: 클로드가 코드를 수정했는데 맘에 안 들 경우, `git checkout` 명령어로 즉시 이전 상태로 복구할 수 있습니다.
*   **설계도 대조**: 원격 저장소(GitHub 등)에 있는 설계도와 현재 로컬 파일의 차이점을 분석하는 데 필수적입니다.

### Git 설치 확인 및 방법 (macOS)

1.  **설치 확인**: 터미널에서 다음 명령어를 입력합니다.
    ```bash
    git --version
    ```
    버전 숫자가 나오면 이미 설치된 것이므로 바로 사용하면 됩니다.

2.  **설치 방법**: `command not found`가 뜬다면 아래 명령어로 설치합니다.
    ```bash
    xcode-select --install
    ```
    이후 나타나는 팝업창에서 **[설치]**를 클릭하면 Git을 포함한 필수 개발 도구들이 설치됩니다.

### Git 초기 설정 (필수)

Git을 처음 설치했다면, 누가 코드를 수정하는지 클로드가 알 수 있도록 이름과 이메일을 등록해야 합니다. 상세한 Git 관리 전략은 **[Git 관리 및 워크플로우 가이드](./06_Git_관리_및_워크플로우_가이드.md)**를 참고하세요.

```bash
git config --global user.name "내이름"
git config --global user.email "내이메일@example.com"
```

💡 **다음 단계**
Git 설치가 완료되었다면, 작업 중이던 폴더로 이동(`cd 폴더경로`)하세요. 해당 폴더가 아직 Git 저장소가 아니라면 `git init`을 입력해 저장소로 만들어주세요. 그다음 `claude`를 실행하면 클로드가 **"오, Git이 있군요! 히스토리를 분석해 드릴까요?"**라며 훨씬 똑똑하게 반응할 겁니다.

## 3. Claude Code CLI 설치

npm을 사용하여 Claude Code를 전역(Global)으로 설치합니다.

```bash
# Claude Code 설치
npm install -g @anthropic-ai/claude-code

# Mac/Linux에서 권한 오류 발생 시
sudo npm install -g @anthropic-ai/claude-code
```

## 3. 초기 설정 및 로그인

설치가 완료되면 `claude` 명령어를 입력하여 인증 과정을 진행합니다.

```bash
# 클로드 실행
claude
```

1. 터미널에 표시되는 일회용 코드를 확인합니다.
2. 자동으로 열리는 브라우저에서 Anthropic 계정으로 로그인합니다.
3. 확인란에 코드를 입력하면 연동이 완료됩니다.

## 4. 주요 명령어 활용 팁

| 명령어 | 설명 |
| :--- | :--- |
| `claude` | 현재 디렉토리에서 대화형 세션 시작 |
| `claude "질문 내용"` | 세션을 열지 않고 바로 질문 및 답변 수행 |
| `claude --help` | 도움말 및 전체 명령어 확인 |
| `exit` 또는 `Ctrl+D` | 클로드 세션 종료 |

### 💡 효율적인 토큰 관리 (.claudeignore)
프로젝트 내의 불필요한 파일(로그, 가상환경 등)을 Claude가 읽지 않도록 `.claudeignore` 파일을 생성하세요. 이는 토큰 소모를 줄이고 응답 속도를 높이는 데 도움이 됩니다.

## 5. 주의사항 및 보안

- **Git 사용 권장**: Claude Code는 실제 파일을 수정할 수 있는 권한을 가집니다. 변경 사항을 추적하고 필요 시 복구할 수 있도록 작업 전에 반드시 Git 커밋을 완료하는 것이 안전합니다.
- **인터넷 연결**: 로컬 LLM(Ollama)과 달리 Anthropic의 API를 사용하므로 인터넷 연결이 필요합니다.
