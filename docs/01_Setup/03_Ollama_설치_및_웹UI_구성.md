# 03. Ollama 설치 및 웹 UI 구성

Ollama를 통해 로컬 LLM 엔진을 구축하고, 편리한 인터페이스를 위한 OpenWebUI를 설정합니다.

## 1. Ollama 설치 및 실행

*주의: 대형 모델(`qwen3-coder-next:q4_K_M`)을 사용하기 전, 반드시 [00. macOS 시스템 최적화](./00_macOS_시스템_최적화.md) 가이드를 따라 GPU 메모리 한계를 확장하시기 바랍니다.*

### Homebrew를 이용한 설치
```bash
# Homebrew 미설치 시 먼저 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Ollama 설치
brew install ollama

# 백그라운드 서비스 시작 (재부팅 시 자동 실행)
brew services start ollama
```

### 설치 확인
```bash
ollama --version
curl http://localhost:11434
```

## 2. 에이전트별 모델 다운로드

Mac M4 Pro 64GB 환경에 최적화된 모델 시리즈를 내려받습니다.

```bash
# Router/Documenter: Qwen 2.5 7B (중계 및 문서화용 - 상주 모델)
ollama pull qwen2.5:7b

# Architect: Qwen3 Coder Next (고성능 설계용)
ollama pull qwen3-coder-next:q4_K_M

# Coder: Qwen3 Coder 32B (고속 코드 생성용)
ollama pull qwen3-coder:32b

# Reviewer: Qwen3 Coder 14B (빠른 검증용)
ollama pull qwen3-coder:14b

# Embedding: 다국어 지원 임베딩 모델 (RAG 속도 및 정확도 향상)
ollama pull bge-m3
```

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
1. 브라우저 접속 후 관리자 계정 생성.
2. **Settings** → **Connections** 이동.
3. **Ollama API URL**에 `http://host.docker.internal:11434` 입력 후 저장.
4. **Settings** → **General** (또는 Documents/Embedding) 이동.
5. **Embedding Model** 설정을 `bge-m3`로 지정.
   * 이렇게 설정하면 RAG를 위해 문서를 업로드할 때 처리 속도와 검색 정확도가 비약적으로 향상됩니다.
6. 이제 메인 화면의 모델 선택 창에서 다운로드한 Qwen3 모델들이 표시됩니다.

### 웹 검색(Web Search) 기능 활성화 (Serper.dev 추천)
1. **API 키 발급**: [Serper.dev](https://serper.dev) 접속 후 가입 (2,500회 무료 크레딧 제공).
2. **Settings** → **Web Search** 이동.
3. `Enable Web Search` 스위치를 On으로 변경.
4. **Search Engine** 항목에서 `Serper`를 선택.
5. **Serper API Key** 입력란에 발급받은 키를 붙여넣고 **Save** 클릭.
6. 이제 채팅창에서 "Searching the web..." 메시지와 함께 실시간 구글 검색 결과를 활용합니다.
   * **Tip**: 답변 하단의 지구본 아이콘을 클릭하여 기능을 켜고 끌 수 있습니다.

## 4. 멀티모달(비전) 지원
이미지 분석이 필요한 경우 비전 전용 모델을 추가로 설치할 수 있습니다.
```bash
# Qwen2-VL 또는 Llama 비전 모델 등
ollama pull qwen2-vl:7b
```
OpenWebUI 대화창에 이미지를 업로드하여 분석 성능을 테스트해보세요.
