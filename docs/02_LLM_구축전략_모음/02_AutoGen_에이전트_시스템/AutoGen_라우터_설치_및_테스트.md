# AutoGen 라우터 설치 및 테스트

## Step 1: 라우터 설치 및 테스트 (15분)

```bash
# 1. 라우터용 디렉토리 생성
mkdir -p ~/autogen-setup
cd ~/autogen-setup

# 2. router.py 저장
# 위에서 제공한 router.py 코드를 여기에 저장
cat > router.py << 'EOF'
# (router.py 전체 코드 붙여넣기)
EOF

# 3. 의존성 설치
pip install fastapi uvicorn httpx pydantic psutil

# 4. 라우터 실행 (새 터미널)
python router.py

# 예상 출력:
# ============================================================
# AutoGen LLM Router 시작
# Ollama Base URL: http://localhost:11434
# Router Port: 8000
# ============================================================
```

## Step 2: 라우터 API 테스트 (10분)

새 터미널에서:

```bash
# 1. 헬스 체크
curl http://localhost:8000/health

# 예상 응답:
# {"status":"healthy","ollama":"connected","memory":{"used_gb":"10.5",...}}

# 2. 모델 목록
curl http://localhost:8000/models | python -m json.tool

# 3. Architect (설계) 테스트
curl -X POST http://localhost:8000/architect \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "간단한 TODO API 설계해줄래",
    "max_tokens": 1000
  }' | python -m json.tool

# 응답 예:
# {
#   "model": "qwen3-coder-next:q4_K_M",
#   "agent": "Architect",
#   "response": "## TODO API 설계\n\n### 요구사항\n...",
#   "latency_ms": 15230,
#   ...
# }
```