"""Task execution endpoint — runs agents (e.g. docs-assistant)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..agents.docs_agent import DocsAgent
from ..auth import authenticate

router = APIRouter(prefix="/v1")

# Registry of available agents
AGENTS = {
    "docs-assistant": DocsAgent,
}

# Simple in-memory task store (replace with DB for persistence)
_tasks: dict[str, dict] = {}


class TaskRequest(BaseModel):
    agent: str
    message: str
    credentials: dict | None = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
    agent: str
    response: str | None = None
    tool_calls_count: int = 0
    created_at: str


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    req: TaskRequest,
    caller: dict = Depends(authenticate),
):
    agent_cls = AGENTS.get(req.agent)
    if not agent_cls:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent: {req.agent}. Available: {list(AGENTS.keys())}",
        )

    agent = agent_cls()
    task_id = str(uuid.uuid4())[:8]

    # Execute synchronously for now (async within the call)
    result = await agent.run(message=req.message, credentials=req.credentials)

    task = {
        "task_id": task_id,
        "status": "completed",
        "agent": req.agent,
        "response": result.get("response"),
        "tool_calls_count": result.get("tool_calls_count", 0),
        "created_at": datetime.now().isoformat(),
        "caller": caller.get("sub"),
    }
    _tasks[task_id] = task

    return TaskResponse(**task)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    _caller: dict = Depends(authenticate),
):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)
