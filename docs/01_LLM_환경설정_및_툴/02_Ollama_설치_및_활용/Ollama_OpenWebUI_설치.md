## Ollama + OpenWebUI 설치

### LM Studio vs Ollama 비교

| 도구 | 인터페이스 | 서버 | 모델 관리 | 24/7/에이전트 적합도 |
|------|------------|------|-----------|---------------------| 
| **LM Studio** | GUI (모델 다운/채팅 쉬움) | HTTP 내장 (localhost:1234) | GGUF 파일 직접 로드 | 초보/테스트 좋음 |
| **Ollama** | CLI (터미널 중심) | http://localhost:11434 | ollama pull 명령 | 서버/에이전트 최고 |

**추천**: 24시간 서버 + 에이전트 연동 = **Ollama**

### Ollama 설치

#### Homebrew를 통한 설치
```bash
brew install ollama
brew services start ollama  # 백그라운드 서비스로 자동 실행
```

#### 설치 확인
```bash
ollama --version
curl http://localhost:11434  # API 확인
```

### 모델 설치

#### 추천 모델 (M4 64GB용)
```bash
# 메인: Llama 4 Scout (17GB)
ollama pull llama4:scout-q4_K_M

# 보조: Gemma3 12B (8GB)
ollama pull gemma3:12b

# 코딩: DeepSeek-Coder V2 (12GB)
ollama pull deepseek-coder-v2:16b

# 옵션: Qwen2.5 32B (한국어 최고)
ollama pull qwen2.5:32b
```

#### 모델 실행 테스트
```bash
ollama run llama4:scout-q4_K_M
# 프롬프트 나타나면 "가족 사진 분석해줘" 입력 후 Ctrl+D로 종료
```

### OpenWebUI + Docker 설정

#### 1. localhost만 바인딩 (외부 접근 차단)
```bash
docker run -d \
  -p 127.0.0.1:3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

**보안 설명**:
- `-p 127.0.0.1:3000:8080`: localhost에서만 접근 가능
- `--restart always`: 재부팅 후 자동 시작
- 같은 맥 내에서만 `http://localhost:3000` 접근 가능

#### 2. 원격 접근이 필요한 경우 (VPN 방식 - 포트 안 열기)

**옵션 A: Tailscale (무료, 권장)**
```bash
# Tailscale 설치
brew install tailscale
tailscale up

# 다른 기기에서: https://[당신의-tailscale-IP]:3000
```

**옵션 B: Cloudflare Tunnel (포트 안 열음, 무료)**
```bash
# Cloudflare CLI 설치
brew install cloudflare/cloudflare/cloudflared

# 터널 실행
cloudflared tunnel --url http://localhost:3000
```

### OpenWebUI 사용

1. 브라우저에서 `http://localhost:3000` 접속
2. 회원가입/로그인
3. Settings → Connections → Ollama API URL: `http://host.docker.internal:11434`
4. 모델 선택 후 채팅 시작