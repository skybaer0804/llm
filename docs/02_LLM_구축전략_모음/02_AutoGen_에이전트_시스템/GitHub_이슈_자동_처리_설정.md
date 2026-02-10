# GitHub 이슈 자동 처리 설정

## Step 4: GitHub 이슈 자동 처리 설정 (30분)

GitHub CLI 설정:

```bash
# 1. GitHub CLI 설치 확인
gh --version

# 2. GitHub 로그인 (처음만)
gh auth login
# → GitHub.com 선택
# → HTTPS 선택
# → PAT(Personal Access Token) 또는 browser login 선택

# 3. 저장소 초기화 (테스트용)
cd ~/autogen-setup
git init
git remote add origin https://github.com/{YOUR_USERNAME}/{YOUR_REPO}.git

# 4. 테스트 이슈 생성
gh issue create \
  --title "TODO API 구현" \
  --body "간단한 TODO API 만들어줄래?"
```

`github_monitor.py` 작성:

```python
"""
GitHub 이슈 모니터 + AutoGen 자동 처리

24시간 이슈 감시 → 자동으로 설계/구현/검수 처리
"""

import subprocess
import json
import time
import logging
from datetime import datetime
from autogen_team import run_autogen_pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_open_issues():
    """GitHub에서 Open 이슈 조회"""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--state=open", "--json=number,title,body,labels"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        logger.error(f"이슈 조회 실패: {e}")
        return []

def process_issue(issue):
    """GitHub 이슈를 AutoGen으로 처리"""
    issue_num = issue["number"]
    title = issue["title"]
    body = issue.get("body", "(내용 없음)")
    
    logger.info(f"이슈 #{issue_num} 처리: {title}")
    
    # AutoGen 파이프라인 실행
    requirement = f"""
🔗 GitHub Issue #{issue_num}

제목: {title}

상세:
{body}

→ 이 이슈를 해결해줄래?
    """
    
    try:
        run_autogen_pipeline(requirement)
        
        # 처리 완료 댓글
        subprocess.run(
            ["gh", "issue", "comment", str(issue_num),
             "-b", "✅ AutoGen 팀이 완료했습니다!\n\n- ✓ 설계 완료\n- ✓ 코드 구현\n- ✓ 코드 검수\n- ✓ 테스트 통과"],
            timeout=10
        )
        logger.info(f"✅ 이슈 #{issue_num} 완료 + 댓글 작성")
        
    except Exception as e:
        logger.error(f"❌ 이슈 #{issue_num} 처리 실패: {e}")
        
        # 에러 댓글
        try:
            subprocess.run(
                ["gh", "issue", "comment", str(issue_num),
                 "-b", f"❌ 처리 중 에러: {str(e)}\n\nHuman 승인 필요합니다."],
                timeout=10
            )
        except:
            pass

def monitor_loop():
    """24시간 모니터링 루프"""
    logger.info("="*60)
    logger.info("GitHub 이슈 모니터 시작!")
    logger.info("="*60)
    
    cycle = 0
    
    while True:
        cycle += 1
        logger.info(f"\n[사이클 {cycle}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        issues = get_open_issues()
        
        if issues:
            logger.info(f"발견: {len(issues)}개 이슈")
            for issue in issues:
                try:
                    process_issue(issue)
                    time.sleep(5)  # 요청 간 간격
                except Exception as e:
                    logger.error(f"처리 중 에러: {e}")
        else:
            logger.info("처리할 이슈 없음")
        
        # 1시간 대기
        logger.info("다음 체크: 1시간 후")
        time.sleep(3600)

if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        logger.info("\n모니터 종료")
```