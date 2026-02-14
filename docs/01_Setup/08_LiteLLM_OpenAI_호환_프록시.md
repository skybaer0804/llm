# 08. LiteLLM – OpenAI 호환 프록시

LiteLLM은 **"세상의 모든 AI 모델(API)을 OpenAI 규격 하나로 통일시켜 주는 통역사(Proxy)"**라고 이해하면 됩니다.

현재 AI 시장에는 OpenAI(GPT), Anthropic(Claude), Google(Gemini), 그리고 Ollama(로컬 LLM) 등 수많은 모델이 있고, 이들은 제각각 호출 방식이 다릅니다. LiteLLM은 이 복잡한 규격들을 중간에서 가로채어 **표준 규격(OpenAI API 형태)**으로 번역해 줍니다.

---

## 1. 왜 LiteLLM을 쓰나요? (핵심 기능)

### 1.1 표준화 (Unified Interface)

| 문제 | 해결 |
| :--- | :--- |
| Antigravity, Continue 등 대부분의 AI 앱은 **OpenAI API 규격**에 최적화되어 있습니다. | LiteLLM을 맥미니에 띄우면, 앱은 LiteLLM을 "GPT-4"인 줄 알고 신호를 보냅니다. |
| 로컬에서 돌아가는 Ollama는 규격이 조금 다릅니다. | LiteLLM이 실시간으로 번역해서 맥미니의 Ollama에게 전달합니다. |

즉, **Ollama를 쓰면서도 OpenAI 호환 클라이언트를 그대로 사용**할 수 있게 됩니다.

### 1.2 멀티 모델 관리 (Model Router)

- 여러 개의 모델을 **하나의 주소**(예: `http://localhost:4000`)로 묶을 수 있습니다.
- "검색이 필요한 질문은 A 모델로, 코딩 질문은 B 모델로 보내라" 같은 **라우팅 규칙**을 정할 수 있습니다.
- 리모컨 하나로 TV, 에어컨, 오디오를 조종하는 것처럼 **한 엔드포인트로 여러 백엔드**를 제어할 수 있습니다.

### 1.3 기능 확장 (Tool / Function Calling)

- **검색 기능(Serper)** 등을 로컬 LLM에 붙일 때 LiteLLM이 매우 유용합니다.
- LLM이 "인터넷 검색이 필요해"라고 판단하면, LiteLLM이 중간에서 그 신호를 받아 **Serper API** 등을 대신 호출하고, 결과만 LLM에게 다시 전달합니다.
- Open WebUI 없이도 Antigravity 같은 클라이언트에서 **로컬 Ollama + 검색 도구** 조합을 쓸 수 있게 됩니다.

---

## 2. 사용자님의 상황에 대입하면?

맥미니(M4)가 **'거대한 AI 서버'**라면, LiteLLM은 그 서버의 **'창구 직원'**입니다.

| 역할 | 비유 | 설명 |
| :--- | :--- | :--- |
| **Antigravity (손님)** | 클라이언트 | "여기 GPT-4 양식으로 질문 하나 할게요. 검색도 좀 해주시고요." |
| **LiteLLM (창구 직원)** | 프록시 | "네! (속으로: 이건 Ollama한테 시키고, 검색은 Serper한테 물어봐야겠다)" |
| **Ollama & Serper (작업자)** | 백엔드 | 각자 맡은 일을 해서 LiteLLM에게 전달 |
| **LiteLLM** | 취합 | 결과를 모아서 Antigravity에게 "GPT가 답변한 것처럼" 전달 |

Tailscale로 맥미니에 원격 접속할 때, **Ollama 직접 주소** 대신 **LiteLLM 주소**를 Antigravity에 넣으면 OpenAI 형식 + 검색 도구까지 한 번에 사용할 수 있습니다.

---

## 3. 관련 앱 추천

LiteLLM과 함께 쓰면 좋은 도구들입니다.

| 앱 이름 | 설명 |
| :--- | :--- |
| **LiteLLM UI (Dashboard)** | LiteLLM의 작동 상태를 웹 브라우저에서 시각적으로 확인하고, 어떤 모델이 얼마나 사용되었는지 관리할 수 있는 관리 도구입니다. |
| **Docker** | LiteLLM을 맥미니에 직접 설치하는 대신, 독립된 환경(컨테이너)에서 안정적으로 실행하고 관리할 수 있게 해 주는 가상화 플랫폼입니다. |

---

## 4. 설치 및 실행 요약

- **Docker 사용 (권장)**: [LiteLLM 공식 문서](https://docs.litellm.ai/docs/)의 Docker 예시를 따라 `litellm` 이미지로 실행합니다. 설정 파일에서 Ollama 백엔드와 Serper 등 도구를 등록할 수 있습니다.
- **로컬 설치**: `pip install litellm` 후 `litellm --config config.yaml` 형태로 실행합니다. 설정 파일에 모델 라우팅과 도구(Tool)를 정의합니다.

상세 옵션(모델별 엔드포인트, Serper API 키 연동 등)은 LiteLLM 공식 문서를 참고하세요.

---

## 관련 문서

- [07. Tailscale 기반 Ollama 원격 접속](./07_Tailscale_기반_Ollama_원격_접속.md) – Antigravity 접속 주소를 Ollama 직접 또는 LiteLLM으로 설정할 때 참고
- [03. Ollama 설치 및 웹 UI 구성](./03_Ollama_설치_및_웹UI_구성.md) – Ollama 및 Open WebUI 기반 웹 검색
- [12. 로컬 LLM 인터넷 연결 및 실시간 지식 확장](../03_AutoGen_Agents/12_로컬_LLM_인터넷_연결_및_실시간_지식_확장.md) – Serper, Function Calling 개념
