# Anti-gravity 및 MCP 연동 가이드

이 가이드는 맥북(Client)의 안티그래비티(Anti-gravity)와 맥미니(Server)의 로컬 모델을 Tailscale 네트워크를 통해 연동하고, MCP(Model Context Protocol)를 활용하는 방법을 설명합니다.

## 1. 네트워크 및 서버 기본 설정

### Tailscale 환경에서의 연동
맥미니와 맥북이 Tailscale로 연결되어 있어야 합니다. 맥북에서 맥미니의 로컬 모델을 불러올 때, `localhost` 대신 맥미니의 **Tailscale IP**를 사용합니다.

*   **맥미니 IP 확인**: 터미널에서 `tailscale ip -4` 입력
*   **연결 주소 (Base URL)**: `http://[맥미니-Tailscale-IP]:4000/v1`

### 맥미니 서버 실행 (LiteLLM)
맥미니에서 LiteLLM 프록시 서버가 실행 중이어야 합니다.
```bash
cd ~/projects/litellm
source .venv/bin/activate
export SERPER_API_KEY=your_api_key_here
litellm --config config.yaml
```

---

## 2. 안티그래비티(Anti-gravity) 상세 설정

안티그래비티 최신 버전은 'Agent' 섹션에서 모델을 정의합니다.

1.  **설정 진입**: `Cmd + ,` 또는 왼쪽 하단 톱니바퀴 아이콘 클릭 -> **Agent** 섹션 선택.
2.  **커스텀 엔드포인트 등록**:
    *   **Provider**: OpenAI Compatible (또는 Add Provider) 선택
    *   **Name**: `MacMini-Local`
    *   **API Base URL**: `http://[맥미니-테일스케일-IP]:4000/v1`
    *   **API Key**: `anything` (LiteLLM 기본값)
    *   **Model Name**: `local-search-model` (config.yaml 설정과 동일하게)
3.  **웹 검색 도구 활성화**: `Enable Agent Web Tools` 또는 `Web Search` 옵션을 **[ON]**으로 설정합니다.

---

## 3. MCP (Model Context Protocol) 연동

MCP는 안티그래비티 에이전트가 맥미니의 기능을 '도구'로서 호출할 수 있게 해주는 표준 인터페이스입니다.

### 설정 파일 수정
맥북의 MCP 설정 파일을 직접 수정하여 맥미니를 연동합니다.
*   **파일 경로**: `~/.gemini/antigravity/mcp_config.json`

```json
{
  "mcpServers": {
    "macmini-ai": {
      "command": "curl",
      "args": [
        "-s",
        "-N",
        "http://[맥미니-테일스케일-IP]:4000/v1/mcp"
      ]
    }
  }
}
```

### 작동 방식
*   안티그래비티의 메인 엔진(Gemini)이 `macmini-ai`를 도구로 인식합니다.
*   "맥미니를 통해 분석해줘"와 같은 요청 시 MCP 서버를 통해 맥미니의 모델을 호출합니다.

---

## 4. 추천 도구 및 앱

| 도구 이름 | 용도 | 비고 |
| :--- | :--- | :--- |
| **Stats** | 시스템 모니터링 | M4 GPU 부하 실시간 확인 |
| **Tailscale** | 네트워크 브릿지 | 모든 기기를 동일 네트워크로 연결 |
| **Raycast** | 스크립트 실행 | `run_ai.sh` 스크립트를 단축키로 실행 |
| **Amphetamine** | 서버 잠자기 방지 | 맥미니가 항상 깨어있도록 관리 |
| **Cursor / Cline** | 개발 전용 IDE | MCP 및 커스텀 모델 연동. Cursor는 localhost를 지원하지 않으므로 [10. ngrok 연동](./10_Cursor_ngrok_로컬_Ollama_연동.md) 참고 |

---

## 5. 문제 해결 (Troubleshooting)
*   **연결 실패**: 맥북에서 `ping [맥미니-IP]`를 통해 네트워크 상태 확인.
*   **방화벽**: 맥미니 시스템 설정 -> 네트워크 -> 방화벽에서 4000번 포트 허용 여부 확인.
*   **MCP 오작동**: 안티그래비티의 내장 웹 검색과 MCP 도구가 충돌할 수 있으므로, 하나만 활성화하여 테스트 권장.
