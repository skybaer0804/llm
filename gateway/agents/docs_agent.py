"""Docs Assistant agent — migrated from docs_assistant.py.

Runs the tool-call loop: LLM generates tool_calls → we execute them via
httpx against the docs API → feed results back until LLM produces a final text response.
"""

import json
import logging

import httpx

from ..config import get_settings
from .base import BaseAgent

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 10
MODEL = "docs-assistant"


class DocsAgent(BaseAgent):
    name = "docs-assistant"

    def __init__(self):
        self.settings = get_settings()

    async def run(self, message: str, credentials: dict | None = None) -> dict:
        email = (credentials or {}).get("email", "")
        password = (credentials or {}).get("password", "")

        messages = [
            {
                "role": "system",
                "content": (
                    f"사용자의 로그인 정보: email={email}, password={password}\n"
                    "사용자가 요청하면 먼저 docs_login을 호출하여 토큰을 획득한 후 작업을 수행하라."
                ),
            },
            {"role": "user", "content": message},
        ]

        token: str | None = None
        tool_calls_count = 0

        async with httpx.AsyncClient(timeout=30) as client:
            for round_num in range(MAX_TOOL_ROUNDS):
                # Call LiteLLM
                resp = await client.post(
                    f"{self.settings.litellm_url}/v1/chat/completions",
                    json={"model": MODEL, "messages": messages, "stream": False},
                )
                if resp.status_code != 200:
                    return {"response": f"LiteLLM error {resp.status_code}: {resp.text}", "tool_calls_count": tool_calls_count}

                choice = resp.json()["choices"][0]
                msg = choice["message"]

                if not msg.get("tool_calls"):
                    return {"response": msg.get("content", ""), "tool_calls_count": tool_calls_count}

                messages.append(msg)

                for tc in msg["tool_calls"]:
                    fn_name = tc["function"]["name"]
                    fn_args = tc["function"]["arguments"]
                    if isinstance(fn_args, str):
                        fn_args = json.loads(fn_args)

                    logger.info(f"[docs-agent] round={round_num+1} tool={fn_name}")
                    tool_calls_count += 1

                    result = await self._execute_tool(client, fn_name, fn_args, token)

                    # Capture login token
                    if fn_name == "docs_login" and isinstance(result, dict) and "token" in result:
                        token = result["token"]

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, ensure_ascii=False),
                    })

        return {"response": "Tool call loop exceeded max rounds.", "tool_calls_count": tool_calls_count}

    async def _execute_tool(self, client: httpx.AsyncClient, name: str, args: dict, token: str | None) -> dict:
        base = self.settings.docs_api_url
        headers = {"Content-Type": "application/json"}
        t = args.get("token") or token
        if t:
            headers["Authorization"] = f"Bearer {t}"

        try:
            match name:
                case "docs_login":
                    r = await client.post(f"{base}/auth/login", json={"email": args["email"], "password": args["password"]}, headers={"Content-Type": "application/json"})
                case "docs_create":
                    r = await client.post(f"{base}/docs", json={"name": args["name"], "type": "FILE", "content": args["content"], "visibility": args.get("visibility", "public")}, headers=headers)
                case "docs_update":
                    body = {}
                    if "content" in args:
                        body["content"] = args["content"]
                    if "name" in args:
                        body["name"] = args["name"]
                    r = await client.put(f"{base}/docs/{args['doc_id']}", json=body, headers=headers)
                case "docs_add_tags":
                    r = await client.put(f"{base}/docs/{args['doc_id']}/tags", json={"node_id": args["doc_id"], "tags": args["tags"]}, headers=headers)
                case "docs_search":
                    r = await client.get(f"{base}/docs/search", params={"q": args["query"]}, headers=headers)
                case "docs_search_by_tag":
                    r = await client.get(f"{base}/docs/search/tags", params={"tag": args["tag"]}, headers=headers)
                case "docs_get":
                    r = await client.get(f"{base}/docs/id/{args['doc_id']}", headers=headers)
                case "docs_delete":
                    r = await client.delete(f"{base}/docs/{args['doc_id']}", headers=headers)
                case "webhook_create":
                    body = {"url": args["url"], "events": args["events"]}
                    if "description" in args:
                        body["description"] = args["description"]
                    r = await client.post(f"{base}/webhooks", json=body, headers=headers)
                case _:
                    return {"error": f"Unknown tool: {name}"}
            return r.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}
