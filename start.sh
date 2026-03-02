#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM MSA System - 원클릭 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LITELLM_DIR="$PROJECT_DIR/litellm"
VENV_DIR="$PROJECT_DIR/.venv"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"; }
fail() { echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"; exit 1; }

# .env 파일 로드
ENV_FILE="$PROJECT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " LLM MSA System Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 1. Ollama 서비스 시작 ──
log "1/8  Ollama 서비스 확인..."
if pgrep -x "ollama" > /dev/null 2>&1; then
    log "     Ollama 이미 실행 중"
else
    log "     Ollama 시작 중..."
    OLLAMA_HOST="0.0.0.0" OLLAMA_NUM_CTX=32768 ollama serve > "$PROJECT_DIR/ollama.log" 2>&1 &
    sleep 3
    if pgrep -x "ollama" > /dev/null 2>&1; then
        log "     Ollama 시작 완료 (PID: $(pgrep -x ollama))"
    else
        fail "Ollama 시작 실패. ollama.log를 확인하세요."
    fi
fi

# ── 2. Ollama 헬스 체크 ──
log "2/8  Ollama 헬스 체크..."
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
log "3/8  Python 가상환경 활성화..."
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
log "4/8  맥미니 Ollama 연결 확인..."
MACMINI_URL="${MACMINI_OLLAMA:-http://127.0.0.1:11434}"
if curl -s --connect-timeout 3 "$MACMINI_URL/api/tags" > /dev/null 2>&1; then
    log "     맥미니 Ollama 연결 성공 ($MACMINI_URL)"
else
    warn "맥미니 Ollama 연결 불가 ($MACMINI_URL) - 로컬 모드로 진행"
fi

# ── 5. dev_repo 디렉토리 확인 ──
log "5/8  작업 디렉토리 확인..."
mkdir -p "$PROJECT_DIR/dev_repo"
log "     dev_repo/ 준비 완료"

# ── 6. LiteLLM 프록시 서버 시작 (내부 전용, :4000) ──
log "6/8  LiteLLM 프록시 서버 시작..."
if lsof -i :4000 > /dev/null 2>&1; then
    log "     LiteLLM 이미 실행 중 (port 4000)"
else
    if [ -d "$LITELLM_DIR" ]; then
        (
            export SERPER_API_KEY="${SERPER_API_KEY:?SERPER_API_KEY가 .env에 설정되지 않았습니다}"
            litellm --config "$LITELLM_DIR/config.yaml" --port 4000 > "$PROJECT_DIR/litellm.log" 2>&1 &
        )
        sleep 3
        if lsof -i :4000 > /dev/null 2>&1; then
            log "     LiteLLM 시작 완료 (http://localhost:4000)"
        else
            warn "LiteLLM 시작 실패. litellm.log를 확인하세요."
        fi
    else
        warn "$LITELLM_DIR 디렉토리 없음 - LiteLLM 건너뜀"
    fi
fi

# ── 7. LLM Gateway 시작 (:8000) ──
log "7/8  LLM Gateway 시작..."
if lsof -i :8000 > /dev/null 2>&1; then
    log "     Gateway 이미 실행 중 (port 8000)"
else
    uvicorn gateway.app:app --host 0.0.0.0 --port 8000 --app-dir "$PROJECT_DIR" > "$PROJECT_DIR/gateway.log" 2>&1 &
    sleep 2
    if lsof -i :8000 > /dev/null 2>&1; then
        log "     Gateway 시작 완료 (http://localhost:8000)"
    else
        warn "Gateway 시작 실패. gateway.log를 확인하세요."
    fi
fi

# ── 8. Tailscale Funnel (Gateway :8000 외부 노출) ──
log "8/8  Tailscale Funnel 시작..."
if ! command -v tailscale > /dev/null 2>&1; then
    warn "tailscale 미설치 - Funnel 건너뜀"
elif tailscale funnel status 2>/dev/null | grep -q ":8000"; then
    log "     Tailscale Funnel 이미 활성화 (port 8000)"
else
    osascript -e '
        tell application "Terminal"
            do script "tailscale funnel 8000"
            activate
        end tell
    ' > /dev/null 2>&1
    log "     Tailscale Funnel 별도 터미널에서 시작됨 (port 8000)"
fi

# ── 완료 ──
TS_HOST=$(tailscale status --json 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get("Self",{}).get("DNSName","macmini").rstrip("."))' 2>/dev/null || echo 'macmini')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e " ${GREEN}시스템 준비 완료${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " Gateway (단일 진입점):"
echo "   http://localhost:8000"
echo "   https://${TS_HOST}:8000  (외부)"
echo ""
echo " API 사용법:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/v1/models"
echo "   curl -X POST http://localhost:8000/v1/tasks \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"agent\":\"docs-assistant\",\"message\":\"문서 검색: 테스트\",\"credentials\":{\"email\":\"...\",\"password\":\"...\"}}'"
echo ""
