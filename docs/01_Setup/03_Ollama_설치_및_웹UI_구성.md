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

# Coder: Qwen3 Coder 30B (고속 코드 생성용)
ollama pull qwen3-coder:30b

# Reviewer: Qwen3 14B (빠른 검증용)
ollama pull qwen3:14b

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

1.  **관리자 계정 생성**: 브라우저 접속(`http://localhost:3000`) 후 첫 번째로 가입하는 계정이 관리자 권한을 가집니다.
2.  **연결 설정 (Connections)**:
    *   **Settings** → **Connections** 이동.
    *   **Ollama API URL**에 `http://host.docker.internal:11434` 입력 후 저장 버튼(새로고침 아이콘) 클릭.
3.  **임베딩 모델 설정 (Embedding Model)**:
    OpenWebUI 인터페이스 업데이트로 설정 위치가 헷갈릴 수 있습니다. 아래 경로를 따라 `bge-m3` 모델을 적용하세요.
    *   **진입 경로**: 왼쪽 하단 **사용자 프로필 이미지/이름 클릭** → **설정 (Settings)** → 좌측 메뉴의 **문서 (Documents)** 탭 클릭.
    *   **설정 방법**:
        *   **임베딩 엔진 (Embedding Engine)**: `Ollama`를 선택하세요. (옵션이 없다면 'Local' 확인 필요)
        *   **임베딩 모델 (Embedding Model)**: 직접 `bge-m3`라고 입력한 뒤, 칸 옆의 **새로고침(화살표 원형 아이콘)** 또는 **다운로드/저장 아이콘**을 클릭하세요.
    *   *Tip: 이렇게 설정하면 RAG를 위해 문서를 업로드할 때 처리 속도와 검색 정확도가 비약적으로 향상됩니다.*
4.  **설정 칸이 안 보일 경우 (관리자 권한)**:
    *   해당 메뉴가 보이지 않는다면 관리자 권한 문제일 수 있습니다. 왼쪽 하단의 **어드민 패널 (Admin Panel)** → **설정 (Settings)** → **문서 (Documents)** 경로로 진입하여 전체적인 모델 변경 권한이 활성화되어 있는지 확인하세요.
5.  이제 메인 화면의 모델 선택 창에서 다운로드한 Qwen3 모델들이 정상적으로 표시됩니다.

### 웹 검색(Web Search) 기능 활성화 (Serper.dev 추천)

#### 1. 기능 설정
1. **API 키 발급**: [Serper.dev](https://serper.dev) 접속 후 가입 (2,500회 무료 크레딧 제공).
2. **Settings** → **Web Search** 이동.
3. `Enable Web Search` 스위치를 On으로 변경.
4. **Search Engine** 항목에서 `Serper`를 선택.
5. **Serper API Key** 입력란에 발급받은 키를 붙여넣고 **Save** 클릭.

#### 2. 채팅에서 사용해보기
설정을 마쳤다면 이제 메인 채팅창으로 가서 테스트해 보세요.

*   **지구본 아이콘 확인**: 메시지 입력창 근처에 지구본 모양 아이콘이 생겼을 겁니다. 이 아이콘이 켜져 있어야 검색을 수행합니다.
*   **질문 던지기**: "오늘 서울 날씨 어때?" 또는 "현재 비트코인 가격 알려줘" 같은 최신 정보를 물어보세요.
*   **작동 확인**: AI가 답변하기 전에 **"Searching the web..."** 이라는 메시지가 뜨면 성공입니다!
*   **Tip**: 답변 하단의 지구본 아이콘을 클릭하여 개별 채팅별로 기능을 켜고 끌 수 있습니다.

## 4. 멀티모달(비전) 지원
이미지 분석이 필요한 경우 비전 전용 모델을 추가로 설치할 수 있습니다.
```bash
# Qwen2-VL 또는 Llama 비전 모델 등
ollama pull qwen2-vl:7b
```
OpenWebUI 대화창에 이미지를 업로드하여 분석 성능을 테스트해보세요.
