# 03. Ollama 설치 및 웹 UI 구성

Ollama를 통해 로컬 LLM 엔진을 구축하고, 편리한 인터페이스를 위한 OpenWebUI를 설정합니다.

## 1. Ollama 설치 및 실행 (분산 환경)

분산 아키텍처 구성을 위해 **MacBook(Gateway)**과 **MacMini(Worker)** 두 기기에 각각 Ollama를 설치해야 합니다.

*주의: 대형 모델(`qwen3-coder-next:q4_K_M`)을 사용하는 MacMini는 반드시 [00. macOS 시스템 최적화](./00_macOS_시스템_최적화.md) 가이드를 따라 GPU 메모리 한계를 확장하시기 바랍니다.*

### Homebrew를 이용한 설치 (두 기기 공통)
```bash
# Ollama 설치
brew install ollama

# 백그라운드 서비스 시작 (재부팅 시 자동 실행)
brew services start ollama
```

### 설치 확인 및 네트워크 허용
원격 호출을 위해 Ollama가 외부 접속을 허용해야 합니다.
```bash
# 환경 변수 설정 (zsh 기준)
echo 'export OLLAMA_HOST="0.0.0.0"' >> ~/.zshrc
source ~/.zshrc

# 서비스 재시작
brew services restart ollama
```

> **Tailscale 등 외부 기기에서 접속**할 때는 `OLLAMA_ORIGINS="*"`도 필요합니다. 휴대폰·맥북 등에서 맥미니 Ollama 접속 방법은 [07. Tailscale 기반 Ollama 원격 접속](./07_Tailscale_기반_Ollama_원격_접속.md)을 참고하세요.

## 2. 노드별 모델 다운로드

각 기기의 역할에 맞는 모델을 다운로드합니다.

### ① MacBook (Gateway Node)
```bash
# 라우팅 및 보안 분석 전용
ollama pull llama3.1:8b
```

### ② MacMini (Worker Node)
```bash
# 핵심 두뇌: 모든 에이전트 작업 수행
ollama pull qwen3-coder-next:q4_K_M

# Embedding: RAG 및 문서 분석용
ollama pull bge-m3
```

> **💡 모델 배치 전략**: MacBook은 가볍고 빠른 `llama3.1:8b`를 상주시균으로써 반응성을 확보하고, MacMini는 64GB 자원을 온전히 `qwen3-coder-next`에 할당하여 최고 품질의 결과물을 얻습니다.

## 3. OpenWebUI 구성 (Docker)

Mac에서 가장 깔끔하게 설치하는 방법은 Docker를 사용하는 것입니다. 브라우저에서 대화형으로 모델을 테스트하고, 실시간 웹 검색 기능을 활용할 수 있습니다.

### 설치 전제
* **Docker Desktop**이 설치되어 있어야 합니다.

### 설치 명령어 (터미널 실행)
```bash
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```
* **접속**: 브라우저에서 `http://localhost:3000` 입력.

### OpenWebUI 초기 설정

1.  **관리자 계정 생성**: 브라우저 접속(`http://localhost:3000`) 후 첫 번째로 가입하는 계정이 관리자 권한을 가집니다.
2.  **연결 설정 (Connections)**:
    *   **Settings** → **Connections** 이동.
    *   **Ollama API URL**에 `http://host.docker.internal:11434` 입력 후 저장 버튼(새로고침 아이콘) 클릭.
3.  **임베딩 모델 설정 (Embedding Model)**:
    *   **진입 경로**: 왼쪽 하단 **사용자 프로필 이미지/이름 클릭** → **설정 (Settings)** → 좌측 메뉴의 **문서 (Documents)** 탭 클릭.
    *   **설정 방법**:
        *   **임베딩 엔진 (Embedding Engine)**: `Ollama`를 선택하세요.
        *   **임베딩 모델 (Embedding Model)**: `bge-m3` 입력 후 새로고침.

## 4. 웹 검색(Web Search) 기능 활성화 (Serper.dev 추천)

1. **Serper.dev** API 키 발급.
2. **Settings** → **Web Search** 이동하여 Serper 선택 및 키 입력.
3. 채팅창의 지구본 아이콘을 활성화하여 사용.
