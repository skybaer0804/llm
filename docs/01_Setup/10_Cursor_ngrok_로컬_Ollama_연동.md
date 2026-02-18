# 10. Cursor + ngrok 로컬 Ollama 연동 가이드

커서(Cursor)에서 `http://localhost` 주소를 직접 사용할 수 없는 이유는 커서의 아키텍처가 **모든 요청을 자사 서버를 거쳐 전달**하기 때문입니다. 따라서 외부(커서 서버)에서 접근 가능한 **HTTPS 터널**을 만들어야 합니다.

가장 간편하고 많이 쓰이는 **ngrok**을 이용한 상세 설정 방법입니다.

---

## 1단계: ngrok 설치 및 가입

### 1.1 ngrok 회원가입

[ngrok 공식 사이트](https://ngrok.com)에서 회원가입 후 로그인합니다.

### 1.2 ngrok 설치 (macOS)

맥북 터미널에서 아래 명령어로 ngrok을 설치합니다.

```bash
brew install ngrok   # Homebrew가 있는 경우
```

### 1.3 Authtoken 등록

사이트 대시보드에 있는 Authtoken을 터미널에 등록합니다.

```bash
ngrok config add-authtoken <본인의_토큰>
```

---

## 2단계: 로컬 모델 서버 실행 (Ollama 기준)

로컬 모델이 먼저 실행 중이어야 합니다.

```bash
# 터미널에서 모델 실행
ollama run qwen3-coder-next:q4_K_M
```

기본적으로 Ollama는 `http://localhost:11434`에서 작동합니다.

---

## 3단계: HTTPS 터널 생성

로컬의 11434 포트를 외부 HTTPS 주소로 연결합니다.

```bash
ngrok http 11434
```

실행 후 화면에 뜨는 **Forwarding 주소**(예: `https://xxxx-xxxx.ngrok-free.app`)를 복사합니다.

---

## 4단계: 커서(Cursor) 설정 적용

커서 앱을 열고 **Settings** (톱니바퀴) > **Models** 탭으로 이동합니다.

| 설정 항목 | 값 |
| :--- | :--- |
| **OpenAI API Key** | 실제 키가 필요 없으므로 `ollama` 또는 `1234` 같은 아무 텍스트나 입력 후 저장 |
| **Override OpenAI Base URL** | 위에서 복사한 ngrok 주소 뒤에 **`/v1`**을 반드시 붙여 입력 |
| **Add Custom Model** | 사용할 모델명(`qwen3-coder-next:q4_K_M`)을 정확히 입력 후 추가 |

**Base URL 예시**: `https://xxxx-xxxx.ngrok-free.app/v1`

**기타 모델 끄기**: 충돌 방지를 위해 기존 GPT-4 등 다른 모델들은 스위치를 꺼두는 것이 좋습니다.

---

## ⚠️ 주의사항

### ngrok 무료 버전

- 터널을 **재시작할 때마다 주소가 바뀝니다**.
- 주소가 바뀌면 커서 설정의 **Base URL도 매번 업데이트**해야 합니다.

### 고정 주소가 필요한 경우

- ngrok 유료 플랜 또는 [LiteLLM + Tailscale](./07_Tailscale_기반_Ollama_원격_접속.md) 기반의 **Antigravity/Continue** 사용을 고려하세요.

### 회사망에서 ngrok 또는 100.x 차단 시

- 회사망에서 ngrok 또는 Tailscale `100.x` 대역이 차단되면 [11. 회사망 로컬 서버 노출 가이드](./11_회사망_로컬_서버_노출_가이드.md)의 **Tailscale Funnel**, **Cloudflare Tunnel** 등을 참고하세요.

---

## 문제 해결 (Troubleshooting)

- **404 Not Found** 에러가 발생하는 경우: ngrok 터널이 11434 포트로 정상 연결되어 있는지 확인하고, Base URL에 `/v1`이 붙어 있는지 검토하세요.
- **모델 인식 실패**: 커서에서 Custom Model 이름이 Ollama 모델명과 정확히 일치하는지 확인하세요.

구체적인 디버깅이 필요하면 터미널에서 `ollama list`로 모델 존재 여부를 먼저 확인하세요.

---

## 관련 문서

- [07. Tailscale 기반 Ollama 원격 접속](./07_Tailscale_기반_Ollama_원격_접속.md) – Cursor 대신 Antigravity/Continue + Tailscale 사용 시
- [11. 회사망 로컬 서버 노출 가이드](./11_회사망_로컬_서버_노출_가이드.md) – 회사망에서 Tailscale Funnel, Cloudflare Tunnel 등 HTTPS 터널 대안
- [08. LiteLLM – OpenAI 호환 프록시](./08_LiteLLM_OpenAI_호환_프록시.md) – OpenAI 형식 엔드포인트 구성
- [09. Anti-gravity 및 MCP 연동 가이드](./09_Anti-gravity_및_MCP_연동_가이드.md) – Tailscale 기반 안티그래비티 연동
