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

## 2. GitHub 이슈 모니터 스크립트 (`monitor.py`)

이 스크립트는 주기적으로 새 이슈를 확인하여 `dev_team.py`를 실행합니다.

```python
import subprocess
import json
import time
import logging
from datetime import datetime

# dev_team.py에서 정의한 실행 함수를 가져온다고 가정
# from dev_team import initiate_dev_cycle

def get_open_issues():
    """상태가 'open'인 이슈 목록을 JSON으로 가져옵니다."""
    result = subprocess.run(
        ["gh", "issue", "list", "--state=open", "--json=number,title,body"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else []

def process_issue(issue):
    print(f"[{datetime.now()}] 이슈 #{issue['number']} 처리 시작: {issue['title']}")
    
    # 에이전트 팀에게 전달할 프롬프트 구성
    task_description = f"GitHub Issue #{issue['number']}\nTitle: {issue['title']}\nBody: {issue['body']}"
    
    # initiate_dev_cycle(task_description) 호출 로직
    # ...
    
    # 처리 완료 후 댓글 작성
    subprocess.run([
        "gh", "issue", "comment", str(issue['number']),
        "-b", "✅ AutoGen 에이전트 팀이 이 이슈에 대한 구현 및 테스트를 완료했습니다."
    ])

if __name__ == "__main__":
    while True:
        issues = get_open_issues()
        for issue in issues:
            # 중복 처리 방지 로직 (예: 특정 라벨이 없는 경우만 처리) 등을 추가 권장
            process_issue(issue)
        
        print("다음 확인까지 1시간 대기...")
        time.sleep(3600)
```

## 3. 자동화 워크플로우 예시

1.  사용자가 프로젝트 저장소에 이슈를 생성합니다. (예: "로그인 시 비밀번호 복잡도 검사 추가")
2.  `monitor.py`가 이를 감지하고 에이전트 팀(`dev_team.py`)에게 임무를 전달합니다.
3.  에이전트 팀이 로컬 디렉토리에서 코드를 작성하고 테스트를 수행합니다.
4.  테스트가 성공하면 에이전트가 코드를 커밋/푸시하거나 PR을 생성하도록 구성할 수 있습니다.
5.  최종적으로 GitHub 이슈에 처리 결과 댓글이 달립니다.
