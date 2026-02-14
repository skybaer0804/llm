# LiteLLM + Serper + 안티그래비티 구축 가이드 (맥미니 M4 64GB)

맥미니 M4(64GB) 환경에서 LiteLLM과 Serper를 결합하여 **안티그래비티(Anti-gravity)**에 연결하는 구체적인 구축 가이드입니다.

> **목표**: 맥미니를 하나의 **'검색 기능이 탑재된 가상 OpenAI 서버'**로 만드는 것.

---

## 1단계: 사전 준비

### 1.1 Ollama 설치 및 모델 다운로드

이미 설치되어 있다면 확인만 해주세요.

| 항목 | 설명 |
| :--- | :--- |
| **추천 모델** | Llama 3.1 70B (M4 64GB라면 충분히 구동 가능) 또는 8B |
| **명령어** | `ollama pull llama3.1:70b` |
| **확인** | `ollama list`로 다운로드 여부 확인 |

### 1.2 Serper API Key 발급

| 항목 | 설명 |
| :--- | :--- |
| **사이트** | [serper.dev](https://serper.dev) |
| **방법** | 가입 후 API Key 복사 |
| **혜택** | 무료 크레딧 제공 (2,500건) |

---

## 2단계: 맥미니에 LiteLLM 설치 및 설정

### 2.1 LiteLLM 설치

```bash
pip install 'litellm[proxy]'
```

### 2.2 설정 파일(config.yaml) 생성

원하는 폴더에 `config.yaml` 파일을 만들고 아래 내용을 복사합니다. **이 설정이 로컬 모델에 검색 기능을 주입하는 핵심**입니다.

```yaml
model_list:
  - model_name: local-search-model
    litellm_params:
      model: ollama/llama3.1:70b
      api_base: http://localhost:11434
      # 검색 도구(Tool) 정의
      tools:
        - type: function
          function:
            name: "search"
            description: "최신 정보나 웹 검색이 필요할 때 사용합니다."
            parameters:
              type: object
              properties:
                query:
                  type: string
                  description: "검색할 키워드"
              required: ["query"]

litellm_settings:
  # LiteLLM이 검색 요청을 가로채서 Serper로 처리
  callbacks: ["serper"]
```

### 2.3 환경 변수 설정 및 서버 실행

```bash
export SERPER_API_KEY=발급받은_키_입력
litellm --config config.yaml
```

서버가 실행되면 **`http://localhost:4000`**이 검색 기능을 갖춘 API 서버가 됩니다.

---

## 3단계: 안티그래비티(Anti-gravity) 연동

### 3.1 모델 추가 설정

| 설정 항목 | 값 |
| :--- | :--- |
| **진입 경로** | Settings > Models (또는 API 설정) |
| **선택** | Add Custom Model |
| **Base URL** | `http://localhost:4000/v1` (외부 iPhone 접속 시 Tailscale IP 사용) |
| **Model Name** | `local-search-model` |
| **API Key** | `anything` (LiteLLM 기본값) |

### 3.2 에이전트 설정

안티그래비티 내의 에이전트가 **Tools** 또는 **Function Calling**을 사용할 수 있도록 옵션을 체크합니다.

---

## 4단계: 모바일(iPhone) 활용

외부에서도 사용하려면 맥미니에 **Tailscale**이 켜져 있어야 합니다.

| 추천 앱 | 활용 방법 |
| :--- | :--- |
| **Pal Chat** | 설정에서 API Base를 `http://[맥미니-Tailscale-IP]:4000/v1`로 변경. 이동 중에도 검색 기능 포함 로컬 LLM 사용 가능. |
| **Enchanted** | 깔끔한 UI. 모델명을 `local-search-model`로 수동 지정하여 사용. |

---

## ⚠️ 주의사항 및 팁

### 성능

- Llama 3.1 70B는 검색 결과 분석·답변 능력이 뛰어나지만, **첫 응답까지 시간이 다소 걸릴 수 있음** (M4 성능 기준으로 충분히 체감 가능한 수준).

### 쿼터 관리

- Serper API는 무료 사용량이 정해져 있음.
- **권장**: 안티그래비티 시스템 프롬프트에 *"꼭 필요한 경우에만 검색 기능을 사용해"*라고 명시하여 불필요한 검색 호출을 줄이세요.

### 동작 확인

1. 터미널에서 `litellm` 서버 실행
2. 안티그래비티에서 **"오늘 날씨 어때?"** 질문
3. 터미널 로그에 **Serper 호출 기록**이 뜨면 정상 동작

---

## 관련 문서

- [12. 로컬 LLM 인터넷 연결 및 실시간 지식 확장](./12_로컬_LLM_인터넷_연결_및_실시간_지식_확장.md) – 원리 및 전략
- [01_Setup 08. LiteLLM – OpenAI 호환 프록시](../01_Setup/08_LiteLLM_OpenAI_호환_프록시.md) – LiteLLM 기본 개념
