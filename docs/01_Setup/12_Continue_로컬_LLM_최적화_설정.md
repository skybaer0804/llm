# 12. Continue 로컬 LLM 최적화 설정 가이드

본 가이드는 **Continue** 확장 프로그램을 사용하여 외부(개인 PC 등)의 로컬 LLM과 안정적으로 연동하고, 코드 편집 및 채팅 기능을 최적화하는 방법을 설명합니다.

---

## 🛠 Continue 설정 (config.yaml)

Continue 설정 파일(`config.yaml`)을 열고 아래 내용을 복사해서 붙여넣으세요.

### 1. Continue config.yaml 최적화 설정

```yaml
name: My Local LLM Config
version: 1.0.0
schema: v1

# 모델 정의: LiteLLM을 통해 개인 PC 모델에 접근합니다.
models:
  # 1. 코드 편집 전용 모델 (tools 없음, 빠른 응답)
  - name: Qwen-Coder (Edit)
    provider: openai
    model: qwen-coder
    apiBase: https://macmini.tailaab9f8.ts.net/v1
    apiKey: sk-local-token

  # 2. 검색 및 채팅용 모델 (Serper 검색 도구 포함)
  - name: Qwen-Search (Chat)
    provider: openai
    model: local-search-model
    apiBase: https://macmini.tailaab9f8.ts.net/v1
    apiKey: sk-local-token

# 자동 완성(Tab) 설정: 타이핑 중 코드를 제안합니다.
tabAutocompleteModel:
  name: Autocomplete
  provider: openai
  model: qwen-coder
  apiBase: https://macmini.tailaab9f8.ts.net/v1

# 기본 컨텍스트 설정: 코드 수정 시 파일 맥락을 더 잘 파악하게 돕습니다.
contextProviders:
  - name: code
  - name: docs
  - name: diff
```

---

## 💡 설정 적용 후 활용 팁

- **모델 선택**: Continue 패널 왼쪽 하단의 모델 드롭다운에서 `Qwen-Coder (Edit)`와 `Qwen-Search (Chat)`를 용도에 맞게 스위칭하며 사용할 수 있습니다.
- **코드 수정 (Apply)**: 수정할 코드를 드래그하고 **Cmd+I**를 누른 뒤, `Qwen-Coder (Edit)` 모델이 선택된 상태에서 명령을 내리세요.
- **검색 활용**: 질문 답변이 필요할 때는 `Qwen-Search (Chat)`를 선택하면 LiteLLM의 Serper 설정이 동작하여 최신 정보를 가져옵니다.

---

## 🚀 향후 파일 접근 및 원격 제어를 위한 확장 앱

| 앱 명칭 | 주요 기능 및 역할 |
| :--- | :--- |
| **Continue** | [2026-02-14] 현재 설정 중인 도구로, 로컬 모델을 활용해 AI 채팅, 코드 수정, 자동 완성을 제공하는 확장 프로그램입니다. |
| **Tailscale Drive** | [2026-02-14] 개인 PC의 특정 폴더를 회사 노트북에서 일반 하드 드라이브처럼 인식하게 해줍니다. 소스코드 외의 일반 파일 접근에 매우 유용합니다. |
| **RustDesk** | [2026-02-14] 원격 데스크톱 앱입니다. VS Code 밖의 작업(GUI 앱 실행, 시스템 설정 등)이 필요할 때 화면을 직접 보며 제어할 수 있습니다. |

---

## ✅ 확인 사항

`config.yaml` 저장 후 Continue 패널에 등록된 모델이 잘 보이나요?
채팅창에 **"test"**라고 입력했을 때 개인 PC의 LiteLLM 터미널에 응답 로그가 찍히는지 확인해 보세요! 성공하면 바로 다음 단계인 원격 파일 관리 세팅으로 넘어가겠습니다.
