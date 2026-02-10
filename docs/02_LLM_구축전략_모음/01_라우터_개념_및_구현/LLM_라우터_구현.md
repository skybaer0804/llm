# LLM 라우터 구현 (router.py)

## router.py - LLM 라우팅 & 작업 분배 엔진

2026년 2월 10일 | M4 Pro 64GB 최적화

```python
"""
AutoGen + Qwen3 에이전트용 LLM 라우터

구성:
- Architect (Planner): qwen3-coder-next:q4_K_M (52GB)
- Coder (Dev1): qwen3-coder:32b (19GB)
- Reviewer (Dev2): qwen3:14b (9GB)

메모리 전략: 순차 실행 (한 번에 최대 2개 모델)
"""

import httpx
import json
import os
import logging
import time
import psutil
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 로깅 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/router.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 설정 및 상수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE", "http://localhost:11434")
ROUTER_PORT = int(os.getenv("ROUTER_PORT", 8000))

# 모델 구성 (메모리 용량, 용도, 역할)
MODEL_CONFIG = {
    "qwen3-coder-next:q4_K_M": {
        "name": "Architect",
        "role": "설계자 (Planner)",
        "memory_gb": 52,
        "type": "architect",
        "context_length": 256000,
        "description": "요구사항 분석, 아키텍처 설계, 장기 컨텍스트 추론",
        "priority": 1  # 가장 중요
    },
    "qwen3-coder:32b": {
        "name": "Coder",
        "role": "개발자 (Dev1)",
        "memory_gb": 19,
        "type": "coder",
        "context_length": 32000,
        "description": "코드 구현, 리팩터링, 기능 개발",
        "priority": 2
    },
    "qwen3:14b": {
        "name": "Reviewer",
        "role": "검수자/테스터 (Dev2/Tester)",
        "memory_gb": 9,
        "type": "reviewer",
        "context_length": 32000,
        "description": "코드 리뷰, 테스트 작성, 버그 지적",
        "priority": 3
    }
}

# 작업 타입별 라우팅 규칙
TASK_ROUTING = {
    # Architect (Qwen3-Coder-Next) 라우팅
    "plan": "qwen3-coder-next:q4_K_M",
    "design": "qwen3-coder-next:q4_K_M",
    "architecture": "qwen3-coder-next:q4_K_M",
    "requirements": "qwen3-coder-next:q4_K_M",
    "strategy": "qwen3-coder-next:q4_K_M",
    
    # Coder (Qwen3-Coder 32B) 라우팅
    "code": "qwen3-coder:32b",
    "implement": "qwen3-coder:32b",
    "refactor": "qwen3-coder:32b",
    "fix": "qwen3-coder:32b",
    "feature": "qwen3-coder:32b",
    "optimize": "qwen3-coder:32b",
    
    # Reviewer (Qwen3 14B) 라우팅
    "review": "qwen3:14b",
    "test": "qwen3:14b",
    "qa": "qwen3:14b",
    "validate": "qwen3:14b",
    "debug": "qwen3:14b",
    "summary": "qwen3:14b"
}

# 기본 라우팅
DEFAULT_MODEL = "qwen3-coder-next:q4_K_M"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 모델
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LLMRequest(BaseModel):
    """LLM 요청 모델"""
    prompt: str
    task_type: str = "general"  # plan, code, review, etc.
    max_tokens: int = 4096
    temperature: float = 0.7
    context: Optional[str] = None  # 추가 컨텍스트
    urgency: str = "normal"  # normal, high, critical

class LLMResponse(BaseModel):
    """LLM 응답 모델"""
    model: str
    agent: str  # Architect, Coder, Reviewer
    response: str
    tokens_generated: int
    latency_ms: float
    memory_used_gb: float
    timestamp: str

class ModelStatus(BaseModel):
    """모델 상태"""
    model_name: str
    loaded: bool
    memory_gb: float
    last_used: Optional[str] = None

class MemoryInfo(BaseModel):
    """메모리 정보"""
    total_gb: float
    used_gb: float
    available_gb: float
    percent_used: float

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 유틸리티 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_system_memory() -> MemoryInfo:
    """시스템 메모리 정보 조회"""
    memory = psutil.virtual_memory()
    return MemoryInfo(
        total_gb=memory.total / (1024**3),
        used_gb=memory.used / (1024**3),
        available_gb=memory.available / (1024**3),
        percent_used=memory.percent
    )

def estimate_tokens(text: str) -> int:
    """토큰 수 추정 (대략 1/4 원칙)"""
    return len(text) // 4

def log_routing_decision(task_type: str, selected_model: str, reason: str):
    """라우팅 결정 기록"""
    logger.info(
        f"[ROUTING] task={task_type} → model={selected_model} | reason={reason}"
    )

def log_model_lifecycle(event: str, model: str, memory_gb: Optional[float] = None):
    """모델 생명주기 이벤트 기록"""
    msg = f"[MODEL] {event}: {model}"
    if memory_gb:
        msg += f" ({memory_gb:.1f}GB)"
    logger.info(msg)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 라우팅 엔진
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LLMRouter:
    """LLM 라우팅 엔진"""
    
    def __init__(self):
        self.currently_loaded_models = {}  # {model_name: load_time}
        self.model_cache = {}
    
    def select_model(self, task_type: str, urgency: str = "normal") -> str:
        """
        작업 타입과 긴급도에 따라 최적 모델 선택
        
        로직:
        1. task_type으로 모델 결정
        2. urgency가 "critical"이면 빠른 모델 고려
        """
        
        # Step 1: task_type 기반 기본 모델 선택
        base_model = TASK_ROUTING.get(task_type.lower(), DEFAULT_MODEL)
        
        # Step 2: 긴급도에 따라 조정
        if urgency == "critical":
            # 긴급한 경우, 가벼운 모델 우선
            if base_model == "qwen3-coder-next:q4_K_M":
                # Architect도 중요하면 그대로, 아니면 Coder로
                if task_type.lower() not in ["plan", "design", "architecture"]:
                    base_model = "qwen3-coder:32b"
        
        reason = f"task_type={task_type}, urgency={urgency}"
        log_routing_decision(task_type, base_model, reason)
        
        return base_model
    
    async def check_memory_and_prepare(self, target_model: str):
        """
        메모리 체크 및 모델 준비
        
        정책:
        - Architect(52GB)는 혼자만 사용
        - Coder(19GB) + Reviewer(9GB) 병렬 가능
        """
        
        memory = get_system_memory()
        target_size = MODEL_CONFIG[target_model]["memory_gb"]
        
        logger.info(f"[MEMORY CHECK] 현재: {memory.used_gb:.1f}/{memory.total_gb:.1f}GB")
        logger.info(f"[MODEL SIZE] {target_model} = {target_size}GB 필요")
        
        # Architect 불러올 때: 다른 모델 모두 언로드
        if target_model == "qwen3-coder-next:q4_K_M":
            if len(self.currently_loaded_models) > 0:
                logger.info("[UNLOAD] Architect를 위해 다른 모델 모두 언로드")
                for model in list(self.currently_loaded_models.keys()):
                    if model != target_model:
                        await self.unload_model(model)
            
            # 충분한 메모리 있는지 체크
            if memory.available_gb < target_size + 5:  # 5GB 여유
                logger.warning(
                    f"⚠️ 메모리 부족! {memory.available_gb:.1f}GB < {target_size}GB "
                    "(시스템 재시작 권장)"
                )
        
        # Coder/Reviewer 불러올 때: Architect는 반드시 언로드
        else:
            if "qwen3-coder-next:q4_K_M" in self.currently_loaded_models:
                logger.info("[UNLOAD] Architect 언로드 (Coder/Reviewer 사용)")
                await self.unload_model("qwen3-coder-next:q4_K_M")
        
        # 메모리 부족 최종 체크
        if memory.available_gb < target_size + 2:
            raise HTTPException(
                status_code=507,
                detail=f"메모리 부족 ({memory.available_gb:.1f}GB/{target_size}GB)"
            )
    
    async def unload_model(self, model_name: str):
        """모델 언로드"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(f"{OLLAMA_BASE_URL}/api/unload/{model_name}")
                if response.status_code == 200:
                    self.currently_loaded_models.pop(model_name, None)
                    log_model_lifecycle("UNLOAD", model_name)
        except Exception as e:
            logger.error(f"[UNLOAD ERROR] {model_name}: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI 애플리케이션
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="AutoGen LLM Router",
    description="Qwen3 에이전트용 지능형 라우터",
    version="2.0"
)

router_engine = LLMRouter()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 엔드포인트: 기본
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """헬스 체크"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}")
            memory = get_system_memory()
            
            return {
                "status": "healthy",
                "ollama": "connected",
                "memory": {
                    "used_gb": f"{memory.used_gb:.1f}",
                    "available_gb": f"{memory.available_gb:.1f}",
                    "percent": memory.percent_used
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/models")
async def list_models() -> Dict[str, Any]:
    """등록된 모델 목록"""
    models = []
    for model_key, config in MODEL_CONFIG.items():
        models.append({
            "model": model_key,
            "name": config["name"],
            "role": config["role"],
            "memory_gb": config["memory_gb"],
            "type": config["type"],
            "description": config["description"],
            "context_length": config["context_length"]
        })
    
    return {
        "models": models,
        "total": len(models),
        "routing_rules": TASK_ROUTING
    }

@app.get("/memory")
async def get_memory() -> MemoryInfo:
    """시스템 메모리 상태"""
    return get_system_memory()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 엔드포인트: 라우팅 (메인)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/route", response_model=LLMResponse)
async def route_request(req: LLMRequest) -> LLMResponse:
    """
    LLM 요청을 적절한 에이전트로 라우팅
    
    프로세스:
    1. 작업 타입으로 모델 선택
    2. 메모리 확인 및 모델 준비
    3. Ollama API 호출
    4. 응답 반환
    """
    
    start_time = time.time()
    memory_before = get_system_memory()
    
    # Step 1: 모델 선택
    selected_model = router_engine.select_model(req.task_type, req.urgency)
    agent_info = MODEL_CONFIG[selected_model]
    
    logger.info(f"[REQUEST] task={req.task_type} → agent={agent_info['name']}")
    
    try:
        # Step 2: 메모리 확인 및 준비
        await router_engine.check_memory_and_prepare(selected_model)
        log_model_lifecycle("LOAD", selected_model, agent_info["memory_gb"])
        
        # Step 3: Ollama 호출
        async with httpx.AsyncClient(timeout=600) as client:
            
            # 프롬프트 구성
            full_prompt = req.prompt
            if req.context:
                full_prompt = f"## 컨텍스트\n{req.context}\n\n## 작업\n{req.prompt}"
            
            logger.info(f"[OLLAMA CALL] model={selected_model}, tokens~{estimate_tokens(full_prompt)}")
            
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": req.temperature,
                    "num_predict": req.max_tokens
                },
                timeout=600
            )
            
            if response.status_code != 200:
                logger.error(f"[OLLAMA ERROR] {response.status_code}: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama error: {response.text}"
                )
            
            data = response.json()
            
            latency_ms = (time.time() - start_time) * 1000
            memory_after = get_system_memory()
            memory_used = memory_after.used_gb - memory_before.used_gb
            
            logger.info(
                f"[RESPONSE] agent={agent_info['name']}, "
                f"latency={latency_ms:.0f}ms, tokens~{data.get('eval_count', 0)}"
            )
            
            return LLMResponse(
                model=selected_model,
                agent=agent_info["name"],
                response=data.get("response", ""),
                tokens_generated=data.get("eval_count", 0),
                latency_ms=latency_ms,
                memory_used_gb=max(0, memory_used),
                timestamp=datetime.now().isoformat()
            )
    
    except httpx.TimeoutException:
        logger.error(f"[TIMEOUT] {selected_model}")
        raise HTTPException(status_code=504, detail="요청 시간 초과")
    
    except Exception as e:
        logger.error(f"[ERROR] {selected_model}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 엔드포인트: 역할별 라우팅 (편의)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/architect")
async def architect_route(req: LLMRequest) -> LLMResponse:
    """Architect(설계자) 직접 호출"""
    req.task_type = "design"
    return await route_request(req)

@app.post("/coder")
async def coder_route(req: LLMRequest) -> LLMResponse:
    """Coder(개발자) 직접 호출"""
    req.task_type = "code"
    return await route_request(req)

@app.post("/reviewer")
async def reviewer_route(req: LLMRequest) -> LLMResponse:
    """Reviewer(검수자) 직접 호출"""
    req.task_type = "review"
    return await route_request(req)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 엔드포인트: 배치 처리 (여러 작업)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/batch")
async def batch_route(requests: list[LLMRequest]) -> Dict[str, Any]:
    """
    배치 요청 처리 (순차)
    
    예: [설계 요청, 코드 요청, 검수 요청] → 순차 실행
    """
    results = []
    
    for i, req in enumerate(requests):
        try:
            logger.info(f"[BATCH] {i+1}/{len(requests)} 처리 중...")
            result = await route_request(req)
            results.append({
                "index": i,
                "status": "success",
                "result": result
            })
        except Exception as e:
            logger.error(f"[BATCH ERROR] {i}: {e}")
            results.append({
                "index": i,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total": len(requests),
        "succeeded": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("AutoGen LLM Router 시작")
    logger.info(f"Ollama Base URL: {OLLAMA_BASE_URL}")
    logger.info(f"Router Port: {ROUTER_PORT}")
    logger.info("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=ROUTER_PORT,
        log_level="info"
    )
```