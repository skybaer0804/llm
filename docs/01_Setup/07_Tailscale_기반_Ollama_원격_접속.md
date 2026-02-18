# 07. Tailscale 기반 Ollama 원격 접속

썬더볼트는 같은 공간의 맥북–맥미니 연결에 최적이지만, **외출 중이거나 휴대폰에서 맥미니 Ollama에 접속**하려면 별도 네트워크가 필요합니다. 여러 시도 끝에 **Tailscale(테일스케일)**이 맥북, 맥미니, 휴대폰을 잇는 가장 튼튼한 뿌리로 검증되었습니다. Cursor의 보안 정책 때문에 맥북 연결은 까다로웠지만, 휴대폰 접속 성공으로 네트워크 망은 완벽하게 구축된 상태입니다.

이 문서는 Tailscale을 이용한 **맥미니 Ollama 원격 접속** 최종 요약입니다.

---

## 1. 기본 인프라 (The Network)

| 항목 | 내용 |
| :--- | :--- |
| **도구** | Tailscale |
| **상태** | 맥미니(서버), 맥북(클라이언트), 휴대폰(클라이언트) 모두 Tailscale 로그인 및 연결 완료 |
| **맥미니 Tailnet IP** | `100.xx.xx.xx` (Tailscale 전용 사설 IP, 기기마다 상이) |
| **효과** | 전 세계 어디서든 Tailscale만 켜져 있으면 집 안의 맥미니에 안전하게 접속 가능 |

### Tailscale 설치 (미설치 시)

```bash
brew install tailscale
tailscale up
```

각 기기(맥미니, 맥북, 휴대폰)에서 동일 Tailscale 계정으로 로그인하면 자동으로 같은 Tailnet에 묶입니다. 맥미니의 Tailnet IP는 Tailscale 앱 또는 `tailscale ip -4`로 확인할 수 있습니다.

---

## 2. 맥미니(서버) 설정 핵심

외부 기기(휴대폰, 맥북 등)의 요청을 허용하려면 **반드시** 아래 환경 변수로 Ollama를 실행해야 합니다.

### 실행 명령어 (맥미니에서)

```bash
OLLAMA_ORIGINS="*" OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

| 환경 변수 | 의미 |
| :--- | :--- |
| **OLLAMA_HOST=0.0.0.0** | 모든 네트워크 인터페이스(Tailscale 포함)에서 수신. 외부에서 들어오는 연결을 허용합니다. |
| **OLLAMA_ORIGINS="*"** | 외부 앱(Reins, Antigravity, Continue 등)의 브라우저/앱 출처를 제한하지 않고 접속을 허용합니다. |

> **참고**: `brew services`로 Ollama를 띄운 경우, 서비스 plist에 위 환경 변수를 넣거나, 터미널에서 위 명령으로 직접 실행하도록 설정해야 합니다. 자세한 방법은 [03. Ollama 설치 및 웹 UI 구성](./03_Ollama_설치_및_웹UI_구성.md) 및 [99_Appendix 02. 분산 추론 및 고급 네트워크 설정](../99_Appendix/02_분산_추론_및_고급_네트워크_설정.md)을 참고하세요.

---

## 3. 기기별 접속 방법 요약

맥미니의 Tailnet IP를 `100.xx.xx.xx`라고 할 때 (실제로는 Tailscale 앱에서 확인한 IP로 교체):

| 기기 | 추천 앱 / 도구 | 접속 주소 (Base URL) | 비고 |
| :--- | :--- | :--- | :--- |
| **아이폰** | Reins (Chat for Ollama) | `http://100.xx.xx.xx:11434` | 광고 없고 깔끔한 무료 앱 |
| **맥북** | Antigravity / Continue | `http://100.xx.xx.xx:11434/v1` | Cursor 대안. 보안 차단 없음 |
| **맥북** (OpenAI 형식 + 검색) | Antigravity 등 | `http://100.xx.xx.xx:4000` (LiteLLM) | OpenAI 규격 + Serper 등 도구 사용 시 [08. LiteLLM](./08_LiteLLM_OpenAI_호환_프록시.md) 참고 |
| **브라우저** | Safari / Chrome | `http://100.xx.xx.xx:11434` | "Ollama is running" 확인용 |

예시: 맥미니 Tailnet IP가 `100.88.99.65`라면  
- 브라우저: `http://100.88.99.65:11434`  
- API 엔드포인트: `http://100.88.99.65:11434/v1`

---

## 4. 최종 결론 및 제언

### 성공한 부분

- **Tailscale을 통한 개인 전용 AI 네트워크 구축 완료.** 맥미니의 전기세만 내면 무제한으로 AI를 쓸 수 있습니다.
- 휴대폰·맥북 등 Tailscale이 켜진 모든 기기에서 동일한 Ollama 서버에 접속 가능합니다.

### Cursor 관련 (권장: Continue 확장 프로그램 사용)

- **Cursor** 에디터의 `Override OpenAI Base URL` 설정은 지연 및 연결 오류 등 '문제가 많으므로' 권장되지 않습니다.
- Cursor 앱 자체 설정 대신 **Continue** 확장 프로그램을 사용하는 것이 훨씬 안정적이며 강력합니다. 상세 설정은 **[12. Continue 로컬 LLM 최적화 설정](./12_Continue_로컬_LLM_최적화_설정.md)** 가이드를 참고하세요.
- 만약 반드시 Cursor 앱 설정을 사용해야 한다면 [10. Cursor + ngrok 로컬 Ollama 연동 가이드](./10_Cursor_ngrok_로컬_Ollama_연동.md)를 참고하여 **ngrok**으로 HTTPS 터널을 구성할 수 있으나 권장하지 않습니다.
- 맥북에서 로컬 LLM을 쓰려면 **Continue** 또는 **Antigravity**를 설치하고, Tailscale로 확인한 맥미니 주소(`http://100.xx.xx.xx:11434`)만 넣으면 바로 작동합니다.

### 향후 계획 요약

- 맥북: Antigravity 또는 VS Code + Continue 설치 후, 위 `100.xx.xx.xx` 주소만 설정하면 Tailscale 경유로 맥미니 Ollama 사용 가능.
- 같은 Tailnet에 있는 다른 기기(태블릿, 다른 PC 등)도 동일한 방식으로 접속할 수 있습니다.

---

## 관련 문서

- [10. Cursor + ngrok 로컬 Ollama 연동 가이드](./10_Cursor_ngrok_로컬_Ollama_연동.md) – Cursor에서 로컬 Ollama 사용 시 ngrok HTTPS 터널 활용
- [11. 회사망 로컬 서버 노출 가이드](./11_회사망_로컬_서버_노출_가이드.md) – Tailscale Funnel, Cloudflare Tunnel 등 회사망 HTTPS 터널 대안
- [02. Docker 및 보안 설정 – Tailscale 소개](./02_Docker_및_보안_설정.md)
- [03. Ollama 설치 및 웹 UI 구성](./03_Ollama_설치_및_웹UI_구성.md)
- [08. LiteLLM – OpenAI 호환 프록시](./08_LiteLLM_OpenAI_호환_프록시.md) (Antigravity에서 OpenAI 형식 + 검색 도구 사용 시)
- [99_Appendix 02. 분산 추론 및 고급 네트워크 설정](../99_Appendix/02_분산_추론_및_고급_네트워크_설정.md) (썬더볼트 + Tailscale 구성 요약)
