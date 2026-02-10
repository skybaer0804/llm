## 3명 개발자 협업 시스템 구현

### 목표 아키텍처

```
GitHub Issue → Planner (설계)
               ↓
            Dev1 (코딩) ← → Dev2 (검수)
               ↓
            Tester (테스트/푸시)
               ↓
            Human (당신) - 승인/결정
```

### 구현 코드

#### 1단계: 필수 라이브러리 설치

```bash
pip install pyautogen ollama python-dotenv
```

#### 2단계: 멀티 에이전트 팀 구성

파일: `autogen_dev_team.py`

```python
import autogen
from typing import Dict, List

# Ollama LLM 설정
llm_config = {
    "config_list": [
        {
            "model": "llama4:scout-q4_K_M",
            "base_url": "http://localhost:11434",
            "api_type": "ollama"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 4096
}

# ==============================
# 에이전트 정의
# ==============================

# 1. Planner (설계자)
planner = autogen.AssistantAgent(
    name="Planner",
    system_message="""
너는 프로젝트 매니저이자 설계자야.
- 요구사항 분석
- 단계별 구현 계획 수립
- 예상 이슈 파악
- 타임라인 제시

항상 명확한 단계와 체크리스트를 제공해.
    """,
    llm_config=llm_config
)

# 2. Developer 1 (시니어 개발자)
dev1 = autogen.AssistantAgent(
    name="Dev1_Senior",
    system_message="""
너는 경험 많은 시니어 개발자야.
- 핵심 기능 구현
- 아키텍처 설계
- 성능 최적화
- 코드 품질 관리

Dev2의 검수 피드백을 참고해서 개선해.
    """,
    llm_config=llm_config
)

# 3. Developer 2 (코드 리뷰어)
dev2 = autogen.AssistantAgent(
    name="Dev2_Reviewer",
    system_message="""
너는 코드 리뷰 전문가야.
- Dev1의 코드 분석
- 보안/성능 문제 지적
- 개선 제안
- Best Practice 적용

항상 건설적이고 구체적인 피드백 제공해.
    """,
    llm_config=llm_config
)

# 4. Tester (QA/테스트)
tester = autogen.AssistantAgent(
    name="Tester_QA",
    system_message="""
너는 QA 엔지니어 겸 배포 담당자야.
- 테스트 시나리오 작성
- pytest 실행
- 버그 추적
- Git push 전 최종 검증

문제 발생 시 개발팀에 보고해.
    """,
    llm_config=llm_config
)

# 5. Human (당신)
human = autogen.UserProxyAgent(
    name="Human_Lead",
    human_input_mode="ALWAYS",
    code_execution_config={
        "work_dir": "./dev_repo",
        "use_docker": False
    }
)

# ==============================
# 그룹 채팅 설정
# ==============================

groupchat = autogen.GroupChat(
    agents=[planner, dev1, dev2, tester, human],
    messages=[],
    max_round=15,
    send_introductions=True
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
    max_consecutive_auto_reply=2
)

# ==============================
# 워크플로 시작
# ==============================

if __name__ == "__main__":
    human.initiate_chat(
        manager,
        message="""
기능 요청: 사용자 로그인 시스템 구현

요구사항:
- JWT 토큰 기반 인증
- 비밀번호 해싱 (bcrypt)
- 리프레시 토큰 지원
- 테스트 커버리지 80% 이상

프로세스:
1. Planner: 설계 및 계획
2. Dev1: 구현
3. Dev2: 코드 리뷰
4. Tester: 테스트 및 git push
5. 문제 발생 시 나(Human)에게 물어보기

시작해!
        """
    )
```

#### 3단계: 24시간 자동 루프 (GitHub 이슈 처리)

파일: `autogen_auto_loop.py`

```python
import autogen
import subprocess
import time
import json
from datetime import datetime

# LLM 설정
llm_config = {
    "config_list": [
        {
            "model": "llama4:scout-q4_K_M",
            "base_url": "http://localhost:11434",
            "api_type": "ollama"
        }
    ]
}

def get_github_issues():
    """GitHub에서 Open 이슈 조회"""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--state=open", "--format=json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"GitHub 이슈 조회 실패: {e}")
        return []

def process_issue(issue):
    """단일 이슈를 AutoGen 팀에 할당"""
    
    planner = autogen.AssistantAgent(
        name="Planner",
        system_message="너는 프로젝트 설계자야.",
        llm_config=llm_config
    )
    
    dev1 = autogen.AssistantAgent(
        name="Dev1_Senior",
        system_message="너는 시니어 개발자야.",
        llm_config=llm_config
    )
    
    dev2 = autogen.AssistantAgent(
        name="Dev2_Reviewer",
        system_message="너는 코드 리뷰어야.",
        llm_config=llm_config
    )
    
    tester = autogen.AssistantAgent(
        name="Tester_QA",
        system_message="너는 QA야. 테스트 후 git push를 시도해.",
        llm_config=llm_config
    )
    
    human = autogen.UserProxyAgent(
        name="Human_Lead",
        human_input_mode="TERMINATE",  # 에러 시만 개입
        code_execution_config={"work_dir": "./dev_repo"}
    )
    
    groupchat = autogen.GroupChat(
        agents=[planner, dev1, dev2, tester, human],
        messages=[],
        max_round=12
    )
    
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    message = f"""
GitHub 이슈 #{issue['number']}: {issue['title']}

내용:
{issue['body']}

이 이슈를 완전히 해결해:
1. 설계 및 계획
2. 구현
3. 코드 리뷰
4. 테스트
5. Git push 후 GitHub에 자동으로 "Fixed" 댓글 달기.
에러 발생 시 나(Human)에게 물어보기.
    """
    
    print(f"\n{'='*60}\n")
    print(f"이슈 처리 시작: #{issue['number']} - {issue['title']}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n\n")
    
    human.initiate_chat(manager, message=message)
    
    print(f"\n이슈 #{issue['number']} 처리 완료!\n")

def main():
    """24시간 메인 루프"""
    print("AutoGen 개발 팀 자동화 시스템 시작!")
    print("GitHub 이슈를 모니터링 중...\n")
    
    cycle = 0
    while True:
        cycle += 1
        print(f"\n[사이클 {cycle}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        issues = get_github_issues()
        
        if issues:
            print(f"발견된 Open 이슈: {len(issues)}개\n")
            
            for issue in issues:
                print(f"처리 중: #{issue['number']}")
                try:
                    process_issue(issue)
                    
                    # GitHub에 완료 댓글
                    subprocess.run(
                        ["gh", "issue", "comment", str(issue['number']), 
                         "-b", "✅ AutoGen 팀이 이 이슈를 완료했습니다."],
                        timeout=10
                    )
                    
                except Exception as e:
                    print(f"⚠️  이슈 #{issue['number']} 처리 중 에러: {e}")
        else:
            print("처리할 이슈 없음. 대기 중...")
        
        print("\n다음 체크: 1시간 후\n")
        time.sleep(3600)

if __name__ == "__main__":
    main()
```

#### 4단계: launchd 데몬으로 자동 실행 (Mac)

파일: `~/Library/LaunchAgents/com.local.autogen.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.local.autogen</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/dev/autogen_auto_loop.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/tmp/autogen.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/autogen_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/dev</string>
</dict>
</plist>
```

설치:
```bash
# YOUR_USERNAME을 본인 계정명으로 변경
launchctl load ~/Library/LaunchAgents/com.local.autogen.plist

# 확인
launchctl list | grep autogen

# 로그 확인
tail -f /tmp/autogen.log
```

### 구현 워크플로 예시

```
1시간마다 체크

GitHub 이슈 발견: "#42: 사용자 프로필 수정 기능"
    ↓
Planner: "요구사항 분석. 1) API 엔드포인트 2) 검증 로직 3) 테스트"
    ↓
Dev1: "코드 작성: PUT /users/{id} 엔드포인트"
    ↓
Dev2: "검수: 비밀번호 해싱 누락 지적, 수정 요청"
    ↓
Dev1: "수정 완료"
    ↓
Tester: "pytest 100% 통과. git push 준비 완료"
    ↓
[Human 개입 필요 시]
"프로덕션 배포 전 승인 필요. DB 마이그레이션 확인했나?"
    ↓
Tester: "확인했습니다. git push 진행"
    ↓
✅ 완료. GitHub에 "Fixed" 댓글 달기
```