# AutoGen 24시간 자동 실행 설정

## Step 5: 24시간 자동 실행 설정 (macOS launchd)

```bash
# 1. launchd 설정 파일 생성
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.autogen.github-monitor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.autogen.github-monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/autogen-setup/github_monitor.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/tmp/autogen-monitor.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/autogen-monitor-error.log</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/autogen-setup</string>
</dict>
</plist>
EOF

# 2. YOUR_USERNAME을 실제 사용자명으로 변경
# macOS에서 확인: whoami

# 3. 데몬 활성화
launchctl load ~/Library/LaunchAgents/com.autogen.github-monitor.plist

# 4. 상태 확인
launchctl list | grep autogen

# 5. 로그 확인
tail -f /tmp/autogen-monitor.log
```

## 🎯 이제 할 수 있는 것들

### 1️⃣ 직접 테스트

```bash
# GitHub 이슈 생성
gh issue create \
  --title "FastAPI + SQLite 연동" \
  --body "POST/GET/PUT/DELETE 모두 구현해줄래?"
```

AutoGen이 자동으로 처리 시작!

### 2️⃣ 로그 모니터링

```bash
# 라우터 로그
tail -f /tmp/router.log

# GitHub 모니터 로그
tail -f /tmp/autogen-monitor.log

# AutoGen 로그
tail -f ~/autogen-setup/autogen.log  # (기본값)
```

### 3️⃣ 성능 모니터링

```bash
# 메모리 사용량
watch -n 1 "ps aux | grep ollama"

# 라우터 API
curl http://localhost:8000/memory | python -m json.tool
```