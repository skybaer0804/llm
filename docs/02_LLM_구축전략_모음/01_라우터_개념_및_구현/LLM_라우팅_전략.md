## LLM 라우팅 전략

### 개념: "똑똑한 라우터 = 3개 LLM을 1개처럼 쓰기"

```text
클라이언트 (웹/IDE/Cursor)
      ↓
[ LLM Router 서버 ]  ← Node/Express/FastAPI
      ↓
 ├── Llama 4 Scout  (메인, 롱컨텍스트)
 ├── Gemma3 12B    (이미지, 보조)
 └── DeepSeek-Coder (코딩 전담)
```

### 라우팅 규칙 테이블

| 요청 특성 | 라우팅 대상 | 이유 |
|---|---|---|
| **일반 대화, 짧은 Q&A (한글)** | Llama 4 Scout | 한국어·추론 최강, 빠름, 무료 |
| **프로젝트 코드 리뷰·리팩터링 (≤100K토큰)** | Llama 4 Scout | 긴 컨텍스트 + 코딩 상위권 |
| **이미지/차트/스캔 PDF 분석** | Gemma3 12B | DocVQA/ChartQA 특화 |
| **문서 번역·요약** | Gemma3 12B | 가볍고 빠르고 정확 |
| **함수 구현, 테스트 코드 생성** | DeepSeek-Coder V2 | 코딩 특화, 속도 빠름 |
| **20K~100K 토큰 초장문 분석** | Llama 4 Scout | MoE 효율, 100K 안정 |
| **150K 이상 "초초장문"** | Llama 4 Scout 우선, 한계 시 Gemini Flash API | Scout는 192K까지 이론, 150K↑는 유료 고려 |
| **박사급 수학·연구 (품질 최우선)** | Gemini 3 Flash API | Frontier급, 비용 감수 필요 |

### 의사 코드 (Node.js)

```ts
app.post('/api/llm', async (req, res) => {
  const { prompt, images = [], taskType, maxLatencyMs } = req.body;

  const tokens = estimateTokens(prompt);      // 대략 토큰 수
  const hasImage = images.length > 0;
  const isCodeTask = ['code', 'refactor', 'test'].includes(taskType);
  const isHardTask = ['math', 'research', 'theorem'].includes(taskType);

  let target: 'scout' | 'gemma' | 'coder' | 'flash';

  if (isHardTask && tokens > 150_000) {
    target = 'flash';                         // 진짜 빡센 초장문 + 추론
  } else if (hasImage) {
    target = 'gemma';                         // 이미지/차트 위주
  } else if (isCodeTask && tokens <= 120_000) {
    target = 'coder';                         // 코드 특화
  } else if (tokens > 180_000) {
    target = 'flash';                         // Scout 한계 넘기
  } else {
    target = 'scout';                         // 기본값
  }

  let answer;
  if (target === 'scout') {
    answer = await callOllama('llama4:scout-q4_K_M', prompt, images);
  } else if (target === 'gemma') {
    answer = await callOllama('gemma3:12b', prompt, images);
  } else if (target === 'coder') {
    answer = await callOllama('deepseek-coder-v2:16b', prompt);
  } else {
    answer = await callGeminiFlash(prompt, images);  // $$ 유료
  }

  res.json({ model: target, answer, tokensUsed: tokens });
});
```

### 실제 구현 (Python FastAPI 버전)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class LLMRequest(BaseModel):
    prompt: str
    images: list = []
    task_type: str = "general"  # general, code, refactor, math, research
    max_tokens: int = 2048

def estimate_tokens(text: str) -> int:
    """대략 토큰 수 추정 (정확하지 않음)"""
    return len(text) // 4

async def call_ollama(model: str, prompt: str, images: list = []) -> str:
    """Ollama 호출"""
    async with httpx.AsyncClient(timeout=300) as client:
        payload = {
            "model": model,
            "prompt": prompt,
            "images": images,
            "stream": False
        }
        response = await client.post(f"{OLLAMA_BASE}/api/generate", json=payload)
        return response.json().get("response", "")

async def call_gemini_flash(prompt: str, images: list = []) -> str:
    """Google Gemini 3 Flash 호출 (유료)"""
    import anthropic
    client = anthropic.Anthropic(api_key=GEMINI_API_KEY)
    message = client.messages.create(
        model="gemini-3-flash",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

@app.post("/api/llm/route")
async def route_llm(req: LLMRequest) -> dict:
    """요청을 적절한 LLM으로 라우팅"""
    tokens = estimate_tokens(req.prompt)
    has_image = len(req.images) > 0
    is_code = req.task_type in ["code", "refactor", "test"]
    is_hard = req.task_type in ["math", "research", "theorem"]
    
    # 라우팅 로직
    if is_hard and tokens > 150_000:
        target = "flash"
    elif has_image:
        target = "gemma"
    elif is_code and tokens <= 120_000:
        target = "coder"
    elif tokens > 180_000:
        target = "flash"
    else:
        target = "scout"
    
    # 호출
    if target == "scout":
        answer = await call_ollama("llama4:scout-q4_K_M", req.prompt, req.images)
    elif target == "gemma":
        answer = await call_ollama("gemma3:12b", req.prompt, req.images)
    elif target == "coder":
        answer = await call_ollama("deepseek-coder-v2:16b", req.prompt)
    else:  # flash
        answer = await call_gemini_flash(req.prompt, req.images)
    
    return {
        "model": target,
        "answer": answer,
        "tokens_estimated": tokens,
        "cost_usd": 0.0 if target != "flash" else round(tokens * 0.00000005, 4)
    }
```

**실행:**
```bash
pip install fastapi uvicorn httpx anthropic
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 호출 예시
curl -X POST http://localhost:8000/api/llm/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "React 훅 설명해줘", "task_type": "general"}'
```