#!/usr/bin/env python3
"""Docs Assistant - 로컬 LLM에 docs API 도구 실행 능력을 부여하는 러너 스크립트.

LiteLLM 프록시의 docs-assistant 모델을 사용하여:
1. 사용자 메시지를 LLM에 전달
2. LLM이 tool call을 반환하면 실제 API 호출 실행
3. 결과를 LLM에 피드백하여 최종 응답 생성
"""

import argparse
import json
import sys

import httpx

BASE_URL = "https://nodnjs-docs.koyeb.app/api"
LITELLM_URL = "http://localhost:4000/v1/chat/completions"
MODEL = "docs-assistant"
MAX_TOOL_ROUNDS = 10


class DocsAssistant:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.token: str | None = None
        self.client = httpx.Client(timeout=30)
        self.messages: list[dict] = []

    def _headers(self, token: str | None = None) -> dict:
        t = token or self.token
        h = {"Content-Type": "application/json"}
        if t:
            h["Authorization"] = f"Bearer {t}"
        return h

    # ── Tool Handlers ──────────────────────────────────────────────

    def _call_login(self, args: dict) -> dict:
        r = self.client.post(
            f"{BASE_URL}/auth/login",
            json={"email": args["email"], "password": args["password"]},
            headers={"Content-Type": "application/json"},
        )
        data = r.json()
        if "token" in data:
            self.token = data["token"]
        return data

    def _call_create(self, args: dict) -> dict:
        body = {
            "name": args["name"],
            "type": "FILE",
            "content": args["content"],
            "visibility": args.get("visibility", "public"),
        }
        r = self.client.post(
            f"{BASE_URL}/docs",
            json=body,
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_update(self, args: dict) -> dict:
        body = {}
        if "content" in args:
            body["content"] = args["content"]
        if "name" in args:
            body["name"] = args["name"]
        r = self.client.put(
            f"{BASE_URL}/docs/{args['doc_id']}",
            json=body,
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_add_tags(self, args: dict) -> dict:
        doc_id = args["doc_id"]
        body = {"node_id": doc_id, "tags": args["tags"]}
        r = self.client.put(
            f"{BASE_URL}/docs/{doc_id}/tags",
            json=body,
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_search(self, args: dict) -> dict:
        r = self.client.get(
            f"{BASE_URL}/docs/search",
            params={"q": args["query"]},
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_search_by_tag(self, args: dict) -> dict:
        r = self.client.get(
            f"{BASE_URL}/docs/search/tags",
            params={"tag": args["tag"]},
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_get(self, args: dict) -> dict:
        r = self.client.get(
            f"{BASE_URL}/docs/id/{args['doc_id']}",
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_delete(self, args: dict) -> dict:
        r = self.client.delete(
            f"{BASE_URL}/docs/{args['doc_id']}",
            headers=self._headers(args.get("token")),
        )
        return r.json()

    def _call_webhook_create(self, args: dict) -> dict:
        body = {
            "url": args["url"],
            "events": args["events"],
        }
        if "description" in args:
            body["description"] = args["description"]
        r = self.client.post(
            f"{BASE_URL}/webhooks",
            json=body,
            headers=self._headers(args.get("token")),
        )
        return r.json()

    TOOL_MAP = {
        "docs_login": "_call_login",
        "docs_create": "_call_create",
        "docs_update": "_call_update",
        "docs_add_tags": "_call_add_tags",
        "docs_search": "_call_search",
        "docs_search_by_tag": "_call_search_by_tag",
        "docs_get": "_call_get",
        "docs_delete": "_call_delete",
        "webhook_create": "_call_webhook_create",
    }

    def execute_tool(self, name: str, args: dict) -> str:
        handler_name = self.TOOL_MAP.get(name)
        if not handler_name:
            return json.dumps({"error": f"Unknown tool: {name}"})
        handler = getattr(self, handler_name)
        try:
            result = handler(args)
            return json.dumps(result, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"error": str(e)})

    # ── LLM Chat Loop ─────────────────────────────────────────────

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        for round_num in range(MAX_TOOL_ROUNDS):
            payload = {
                "model": MODEL,
                "messages": self.messages,
                "stream": False,
            }

            resp = self.client.post(LITELLM_URL, json=payload)
            if resp.status_code != 200:
                return f"[LiteLLM Error {resp.status_code}] {resp.text}"

            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]

            # LLM이 tool call 없이 텍스트로 응답한 경우 → 최종 응답
            if not msg.get("tool_calls"):
                self.messages.append(msg)
                return msg.get("content", "")

            # tool call 처리
            self.messages.append(msg)

            for tc in msg["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args_raw = tc["function"]["arguments"]
                if isinstance(fn_args_raw, str):
                    fn_args = json.loads(fn_args_raw)
                else:
                    fn_args = fn_args_raw

                print(f"  🔧 [{round_num+1}] {fn_name}({json.dumps(fn_args, ensure_ascii=False)[:120]})")

                result = self.execute_tool(fn_name, fn_args)

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        return "[Error] Tool call 루프가 최대 횟수를 초과했습니다."

    def close(self):
        self.client.close()


def main():
    parser = argparse.ArgumentParser(description="Docs Assistant - 로컬 LLM docs API 도구 러너")
    parser.add_argument("--email", required=True, help="로그인 이메일")
    parser.add_argument("--password", required=True, help="로그인 비밀번호")
    parser.add_argument("--message", "-m", help="단발 메시지 (지정하지 않으면 대화형 모드)")
    args = parser.parse_args()

    assistant = DocsAssistant(args.email, args.password)

    # 자동 로그인 컨텍스트를 시스템 메시지로 주입
    assistant.messages.append({
        "role": "system",
        "content": (
            f"사용자의 로그인 정보: email={args.email}, password={args.password}\n"
            "사용자가 요청하면 먼저 docs_login을 호출하여 토큰을 획득한 후 작업을 수행하라."
        ),
    })

    try:
        if args.message:
            # 단발 모드
            response = assistant.chat(args.message)
            print(f"\n{response}")
        else:
            # 대화형 모드
            print("📄 Docs Assistant (종료: quit/exit)")
            print("=" * 50)
            while True:
                try:
                    user_input = input("\n> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not user_input or user_input.lower() in ("quit", "exit"):
                    break
                response = assistant.chat(user_input)
                print(f"\n{response}")
    finally:
        assistant.close()


if __name__ == "__main__":
    main()
