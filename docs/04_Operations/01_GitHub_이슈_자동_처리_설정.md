# 01. GitHub 이슈 자동 처리 설정

GitHub CLI(`gh`)를 활용하여 저장소의 이슈를 에이전트 팀이 자동으로 감지하고 해결하는 파이프라인을 구축합니다.

## 1. 사전 준비 (GitHub CLI 설정)

에이전트가 GitHub과 소통하기 위해 인증이 필요합니다.

```bash
# 1. GitHub CLI 설치
brew install gh

# 2. 로그인 및 인증
gh auth login
# → GitHub.com 선택
# → HTTPS 선택
# → 브라우저 로그인 또는 PAT(Personal Access Token) 선택

# 3. 권한 확인
gh auth status
```

## 2. GitHub 이슈 모니터 및 컨트롤러 스크립트 (`monitor.py`)

이 스크립트는 단순히 이슈를 감지하는 것을 넘어, **상태 관리 및 예외 처리 로직(Controller)**을 포함하여 시스템의 안정성을 보장합니다.

```python
import subprocess
import json
import time
import logging
from datetime import datetime

class AgentController:
    def __init__(self):
        self.quota_status = "HEALTHY"  # HEALTHY, HOLD, PERMANENT_LIMIT

    def check_system_readiness(self):
        """에이전트 실행 전 시스템 및 쿼터 상태 체크"""
        if self.quota_status == "PERMANENT_LIMIT":
            logging.error("🚨 계정 제한 상태입니다. 수동 확인이 필요합니다.")
            return False
        return True

    def handle_error(self, error_message, issue_number):
        """사용자 지침(2026-02-11) 반영: 에러 핸들링 정책"""
        if "rate_limit" in error_message or "429" in error_message:
            self.quota_status = "HOLD"
            self.report_to_github(issue_number, "⏳ API 할당량 초과로 인해 대기 중입니다.")
        elif "expired" in error_message or "unauthorized" in error_message:
            self.quota_status = "PERMANENT_LIMIT"
            self.add_label(issue_number, "critical: agent-stopped")
            self.report_to_github(issue_number, "❌ 에이전트 권한 만료로 작업이 중단되었습니다.")

    def report_to_github(self, issue_number, message):
        subprocess.run(["gh", "issue", "comment", str(issue_number), "-b", message])

    def add_label(self, issue_number, label):
        subprocess.run(["gh", "issue", "edit", str(issue_number), "--add-label", label])

def get_open_issues():
    """상태가 'open'인 이슈 목록을 JSON으로 가져옵니다."""
    result = subprocess.run(
        ["gh", "issue", "list", "--state=open", "--json=number,title,body"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else []

def process_issue(issue, controller):
    if not controller.check_system_readiness():
        return

    print(f"[{datetime.now()}] 이슈 #{issue['number']} 처리 시작")
    
    try:
        # 실제 에이전트 실행 로직 (예: dev_team.py 호출)
        # result = run_agent_team(issue)
        pass
    except Exception as e:
        controller.handle_error(str(e), issue['number'])

if __name__ == "__main__":
    controller = AgentController()
    while True:
        if controller.quota_status == "HOLD":
            print("대기 모드(HOLD)... 1시간 후 재시도합니다.")
            time.sleep(3600)
            controller.quota_status = "HEALTHY" # 재시도를 위해 상태 초기화
            continue

        issues = get_open_issues()
        for issue in issues:
            process_issue(issue, controller)
        
        time.sleep(3600)
```

## 3. 핵심 운영 전략

1.  **순수 기능적 관점**: 페르소나 없이 시스템의 효율성과 안정성에만 집중합니다.
2.  **Hold vs Action**: 임시 쿼터 제한 시에는 '대기(Hold)', 영구적 만료 시에는 '중단 및 보고(Action)'를 수행합니다.
3.  **파일 기반 상태 관리**: SQLite 대신 Git 로그와 이슈/PR 상태를 활용하여 맥미니-맥북 간의 상태를 동기화합니다.

## 3. 자동화 워크플로우 예시

1.  사용자가 프로젝트 저장소에 이슈를 생성합니다. (예: "로그인 시 비밀번호 복잡도 검사 추가")
2.  `monitor.py`가 이를 감지하고 에이전트 팀(`dev_team.py`)에게 임무를 전달합니다.
3.  에이전트 팀이 로컬 디렉토리에서 코드를 작성하고 테스트를 수행합니다.
4.  테스트가 성공하면 에이전트가 코드를 커밋/푸시하거나 PR을 생성하도록 구성할 수 있습니다.
5.  최종적으로 GitHub 이슈에 처리 결과 댓글이 달립니다.
