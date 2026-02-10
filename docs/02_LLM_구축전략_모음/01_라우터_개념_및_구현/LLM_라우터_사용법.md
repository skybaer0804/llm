# LLM 라우터 사용법

## 🚀 사용법

### 1️⃣ 설치 및 실행

```bash
# 필수 라이브러리 설치
pip install fastapi uvicorn httpx pydantic psutil

# 라우터 실행
python router.py
```

### 2️⃣ 작업 요청 예시

#### A. Architect (설계) 호출

```python
import httpx

response = httpx.post(
    "http://localhost:8000/route",
    json={
        "prompt": """
마이크로서비스 아키텍처 설계
- User Service, Order Service, Product Service
- gRPC 통신
- PostgreSQL + Redis

→ 전체 구조 설계 + 단계별 구현 계획 수립
        """,
        "task_type": "design",
        "urgency": "normal"
    }
)
print(response.json())
```

응답 예:
```json
{
  "model": "qwen3-coder-next:q4_K_M",
  "agent": "Architect",
  "response": "## 마이크로서비스 아키텍처 설계\n\n### 1단계: 요구사항 분석\n...",
  "tokens_generated": 1024,
  "latency_ms": 45230,
  "memory_used_gb": 2.1,
  "timestamp": "2026-02-10T12:49:00"
}
```

#### B. Coder (구현) 호출

```python
response = httpx.post(
    "http://localhost:8000/coder",
    json={
        "prompt": """
User Service 구현 (FastAPI)
- JWT 인증
- PostgreSQL 연동
- 비밀번호 해싱

완성된 코드 작성
        """,
        "max_tokens": 2048
    }
)
```

#### C. Reviewer (검수) 호출

```python
response = httpx.post(
    "http://localhost:8000/reviewer",
    json={
        "prompt": """
다음 코드를 리뷰해주세요:

@app.post(\"/login\")
async def login(username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.verify(password, user.hashed_password):
        token = jwt.encode({\"sub\": user.id}, SECRET_KEY)
        return {\"token\": token}

버그, 보안, 성능 이슈 지적
        """,
        "task_type": "review"
    }
)
```

#### D. 배치 처리 (설계 → 구현 → 검수)

```python
batch_requests = [
    {
        "prompt": "마이크로서비스 설계...",
        "task_type": "design"
    },
    {
        "prompt": "User Service 코드 작성...",
        "task_type": "code"
    },
    {
        "prompt": "코드 리뷰...",
        "task_type": "review"
    }
]

response = httpx.post(
    "http://localhost:8000/batch",
    json=batch_requests
)

print(response.json())
# {
#   "total": 3,
#   "succeeded": 3,
#   "failed": 0,
#   "results": [...]
# }
```