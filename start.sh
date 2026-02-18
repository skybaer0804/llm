#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM 멀티 에이전트 시스템 - 재부팅 후 원클릭 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/startup.log"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"; }
fail() { echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"; exit 1; }

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " LLM Agent System Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Ollama 서비스 시작 (MacBook) ──
log "1/5  Ollama 서비스 확인..."
if pgrep -x "ollama" > /dev/null 2>&1; then
    log "     Ollama 이미 실행 중"
else
    log "     Ollama 시작 중..."
    OLLAMA_HOST="0.0.0.0" ollama serve > "$PROJECT_DIR/ollama.log" 2>&1 &
    sleep 3
    if pgrep -x "ollama" > /dev/null 2>&1; then
        log "     Ollama 시작 완료 (PID: $(pgrep -x ollama))"
    else
        fail "Ollama 시작 실패. ollama.log를 확인하세요."
    fi
fi

# ── 2. Ollama 헬스 체크 ──
log "2/5  Ollama 헬스 체크..."
RETRY=0
MAX_RETRY=10
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRY ]; then
        fail "Ollama가 응답하지 않습니다 (${MAX_RETRY}회 시도)"
    fi
    sleep 1
done
log "     Ollama 정상 응답 확인"

# ── 3. 가상환경 활성화 ──
log "3/5  Python 가상환경 활성화..."
if [ ! -d "$VENV_DIR" ]; then
    warn "가상환경이 없습니다. 생성 중..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip > /dev/null 2>&1
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r "$PROJECT_DIR/requirements.txt" > /dev/null 2>&1
    fi
else
    source "$VENV_DIR/bin/activate"
fi
log "     Python: $(python --version) | venv: $VIRTUAL_ENV"

# ── 4. 맥미니 Ollama 연결 확인 ──
log "4/5  맥미니 Ollama 연결 확인..."
MACMINI_URL="${MACMINI_OLLAMA:-http://127.0.0.1:11434}"
if curl -s --connect-timeout 3 "$MACMINI_URL/api/tags" > /dev/null 2>&1; then
    log "     맥미니 Ollama 연결 성공 ($MACMINI_URL)"
else
    warn "맥미니 Ollama 연결 불가 ($MACMINI_URL) - 로컬 모드로 진행"
fi

# ── 5. dev_repo 디렉토리 확인 ──
log "5/5  작업 디렉토리 확인..."
mkdir -p "$PROJECT_DIR/dev_repo"
log "     dev_repo/ 준비 완료"

# ── 완료 ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e " ${GREEN}시스템 준비 완료${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " 사용법:"
echo "   python main.py \"요구사항\" --no-docker"
echo "   python main.py \"요구사항\" --mode groupchat --no-docker"
echo ""
echo " 라우터 서버 시작:"
echo "   uvicorn router:app --host 0.0.0.0 --port 8000"
echo ""
