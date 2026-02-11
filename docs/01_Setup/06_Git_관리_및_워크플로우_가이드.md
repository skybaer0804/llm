# 06. Git 관리 및 워크플로우 가이드

로컬 LLM 프로젝트와 같이 여러 에이전트가 협업하고 복잡한 로직이 얽혀 있는 경우, Git은 단순한 저장소를 넘어 프로젝트의 안정성과 연속성을 보장하는 핵심 도구입니다.

## 1. Git 관리가 꼭 필요한 이유

*   **진행 상황의 이정표 (Checkpoints)**: Claude Code 등 AI 도구가 작업을 하다가 사용량 제한(Usage Limit)으로 멈췄을 때, 작업 단위별로 `git commit`이 되어 있다면 나중에 해당 지점부터 수월하게 이어서 작업할 수 있습니다.
*   **안전한 코드 수정**: AI가 코드를 대량으로 수정했을 때, 예상치 못한 버그가 발생하거나 결과가 만족스럽지 않다면 `git checkout` 명령 한 번으로 즉시 이전 상태로 되돌릴 수 있습니다.
*   **AI의 문맥 파악 능력 향상**: Claude Code CLI는 Git 히스토리(`git log`, `git diff`)를 읽어 현재 작업의 맥락을 파악합니다. Git이 설정되어 있어야 AI가 "이전에 `config.py`를 수정했으니 이제 `agents.py`를 수정할 차례군요"라고 스스로 판단할 수 있습니다.
*   **설계도와의 동기화**: `llm` 저장소에 있는 설계도와 로컬 코드를 비교하며 작업할 수 있어 구현 누락을 방지하고 일관성을 유지합니다.

## 2. 관리 대상 및 제외 파일 설정

모든 코드를 Git으로 관리하되, 보안과 저장 공간 효율성을 위해 제외해야 할 파일들을 지정해야 합니다.

| 분류 | 파일 예시 | 처리 방법 |
| :--- | :--- | :--- |
| **핵심 코드** | `agents.py`, `config.py`, `router.py`, `gpu_config.py` | 반드시 포함 (`git add`) |
| **설정/환경** | `.env` (API Key 등 포함), `.venv/` (가상환경) | 제외 (`.gitignore` 등록) |
| **임시 파일** | `/tmp/router.log`, `shared/temp_context.json` | 제외 (`.gitignore` 등록) |
| **실행 결과** | `dev_repo/` (에이전트가 생성한 결과물) | 선택적 포함 |

### .gitignore 예시
```text
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
.env

# Logs and databases
*.log
*.sqlite

# OS files
.DS_Store
```

## 3. 추천 작업 워크플로우 (Workflow)

효율적인 협업과 복구를 위해 아래 순서대로 작업하는 습관을 권장합니다.

1.  **작업 전 상태 확인**: `git status`로 현재 작업 디렉토리가 깨끗한지 확인합니다.
2.  **Claude 작업 시작**: `claude`를 실행하여 특정 기능 구현이나 수정을 요청합니다.
3.  **검토 및 커밋**: AI가 수정한 내용이 의도대로 동작한다면 세션을 종료하고 커밋합니다.
    ```bash
    git add .
    git commit -m "feat: agents.py 에이전트 정의 완료"
    ```
4.  **원격 저장소 백업**: 주요 작업 단락이 끝날 때마다 GitHub 등 원격 저장소로 푸시합니다.
    ```bash
    git push origin main
    ```

## 4. .claudeignore 활용 팁

프로젝트 규모가 커지면 Claude가 불필요한 파일(로그, 대규모 라이브러리 등)까지 읽느라 토큰을 낭비할 수 있습니다. `.gitignore`와 유사하게 `.claudeignore` 파일을 만들어 관리하면 AI가 무시할 경로를 지정하여 토큰 효율을 높일 수 있습니다.

```text
# .claudeignore 예시
node_modules/
.venv/
docs/old/
*.log
```

---
💡 **팁**: 지금 바로 `git status`를 입력하여 커밋되지 않은 코드들이 있는지 확인해 보세요. 작업 중단 시 소중한 코드를 지키는 가장 좋은 방법은 수시로 커밋하는 것입니다.
