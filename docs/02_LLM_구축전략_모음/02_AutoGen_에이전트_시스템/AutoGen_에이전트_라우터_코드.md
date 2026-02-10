## 🎯 이 라우터의 핵심 기능

### 1️⃣ **작업 타입별 자동 라우팅**

```python
# 예시: 자동 라우팅 규칙

"design" → Qwen3-Coder-Next (52GB, Architect)
"code" → Qwen3-Coder 32B (19GB, Coder)
"review" → Qwen3 14B (9GB, Reviewer)
```


### 2️⃣ **메모리 자동 관리**

```python
# Architect 불러올 때
1. 다른 모든 모델 언로드
2. 52GB 여유 확인
3. 로드 후 작업

# Coder/Reviewer 불러올 때
1. Architect 언로드
2. 19GB + 9GB = 28GB 확인
3. 병렬 실행 가능
```


### 3️⃣ **편리한 API 엔드포인트**

```bash
# 직접 호출
curl -X POST http://localhost:8000/architect \
  -H "Content-Type: application/json" \
  -d '{"prompt": "설계해줄래?"}'

# 배치 처리 (설계 → 구현 → 검수)
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '[{...}, {...}, {...}]'
```


***

## 📋 요청 예시 (Python)

### 시나리오: 마이크로서비스 구축

```python
import httpx

# 1️⃣ Architect: 설계 단계
arch_response = httpx.post(
    "http://localhost:8000/architect",
    json={
        "prompt": """
마이크로서비스 설계:
- User Service (JWT 인증)
- Order Service (주문 처리)
- Product Service (상품 관리)
- gRPC 통신, PostgreSQL, Redis

→ 전체 아키텍처 + 단계별 구현 계획
        """,
        "max_tokens": 3000
    }
).json()

print(f"Architect 응답 (소요시간: {arch_response['latency_ms']}ms)")
print(arch_response['response'][:500])  # 첫 500자

# 2️⃣ Coder: 구현 단계
code_response = httpx.post(
    "http://localhost:8000/coder",
    json={
        "prompt": f"""
User Service 구현 (FastAPI):

요구사항:
- JWT 토큰 기반 인증
- 비밀번호 bcrypt 해싱
- PostgreSQL 연동
- Redis 캐싱

아키텍처 컨텍스트:
{arch_response['response'][:1000]}

→ 완성된 코드 작성
        """,
        "max_tokens": 2500
    }
).json()

print(f"\nCoder 응답 (소요시간: {code_response['latency_ms']}ms)")

# 3️⃣ Reviewer: 검수 단계
review_response = httpx.post(
    "http://localhost:8000/reviewer",
    json={
        "prompt": f"""
다음 코드를 리뷰해주세요:

{code_response['response'][:2000]}

체크 항목:
- 보안 취약점
- SQL 인젝션
- 에러 핸들링
- 성능 최적화
- 테스트 필요성

→ 문제점 + 개선안 제시
        """,
        "task_type": "review"
    }
).json()

print(f"\nReviewer 응답 (소요시간: {review_response['latency_ms']}ms)")
print(review_response['response'])
```


***

## 🚀 AutoGen에서 사용하기

### autogen_team.py에 라우터 통합

```python
from autogen import AssistantAgent, GroupChat, GroupChatManager

# LLM 라우터로 연결
llm_config = {
    "config_list": [
        {
            "model": "gpt-4",  # 이름은 상관없음
            "base_url": "http://localhost:8000",  # 라우터 포트
            "api_type": "openai",
            "api_key": "dummy-key"
        }
    ]
}

# Architect 에이전트
architect = AssistantAgent(
    name="Architect",
    system_message="당신은 마이크로서비스 설계자입니다. 요구사항을 받아 아키텍처를 설계하세요.",
    llm_config=llm_config
)

# Coder 에이전트
coder = AssistantAgent(
    name="Coder",
    system_message="당신은 시니어 개발자입니다. 설계에 따라 코드를 구현하세요.",
    llm_config=llm_config
)

# Reviewer 에이전트
reviewer = AssistantAgent(
    name="Reviewer",
    system_message="당신은 코드 리뷰어입니다. 보안, 성능, 스타일을 검수하세요.",
    llm_config=llm_config
)

# 그룹 채팅 설정
groupchat = GroupChat(
    agents=[architect, coder, reviewer],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# 이슈 처리 시작
user = UserProxyAgent(name="User", human_input_mode="TERMINATE")
user.initiate_chat(
    manager,
    message="마이크로서비스 아키텍처 구현해줄래?"
)
```


***

## 📊 로깅 \& 모니터링

라우터는 자동으로 로그를 남깁니다:

```bash
# 실시간 로그 확인
tail -f /tmp/router.log

# 샘플 로그 출력
2026-02-10 12:49:00 - router - INFO - [ROUTING] task=design → model=qwen3-coder-next:q4_K_M | reason=task_type=design, urgency=normal
2026-02-10 12:49:01 - router - INFO - [MEMORY CHECK] 현재: 15.2/64GB
2026-02-10 12:49:01 - router - INFO - [MODEL] LOAD: qwen3-coder-next:q4_K_M (52GB)
2026-02-10 12:49:45 - router - INFO - [RESPONSE] agent=Architect, latency=44230ms, tokens~1024
2026-02-10 12:50:00 - router - INFO - [MODEL] UNLOAD: qwen3-coder-next:q4_K_M
2026-02-10 12:50:01 - router - INFO - [ROUTING] task=code → model=qwen3-coder:32b | reason=task_type=code, urgency=normal
```


***

## ✅ 정리: 전체 파일 구성

이제 당신이 준비해야 할 파일들:

```
your-project/
├── router.py                  # ⭐ 새로 만든 라우터 (이 파일)
├── autogen_team.py            # AutoGen 에이전트 팀 설정
├── docker-compose.yml         # Docker 설정 (기존 문서)
├── M4-Pro-AutoGen-Setup.md    # 설정 가이드
└── 📄 M4-Pro-Optimal-3LLM.md  # LLM 선택 가이드 (updated)
```


***

**✨ 완료!** 이제 당신의 시스템은:

✅ **Qwen3-Coder-Next** (Architect, 설계)
✅ **Qwen3-Coder 30B** (Coder, 구현)
✅ **Qwen3 14B** (Reviewer, 검수)
✅ **라우터가 자동으로 메모리 관리** (순차 + 병렬 최적화)
✅ **AutoGen 완전 자동화** (GitHub 이슈 → 자동 처리)

모두 M4 Pro 64GB에서 **무료로 24/7 운영 가능**합니다! 🚀

아무거나 궁금한 거 있으면 더 물어봐요!
