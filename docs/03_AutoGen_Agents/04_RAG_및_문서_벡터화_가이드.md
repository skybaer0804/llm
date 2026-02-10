# 04. RAG 및 문서 벡터화 가이드

에이전트가 최신 라이브러리 용법이나 프로젝트 전용 스킬(`vercel-agent-skill`)을 정확히 이해하게 하려면 **RAG(Retrieval-Augmented Generation)** 시스템 구축이 필수적입니다.

---

## 1. 벡터화(Vectorization)란?

### 1. 벡터화란?
텍스트(언어)를 컴퓨터가 수학적으로 연산할 수 있는 **숫자 배열(Vector)**로 변환하는 과정을 말합니다. 단순한 키워드 매칭이 아니라 문장의 '의미'를 숫자로 수치화하는 것이 핵심입니다.

#### 왜 하는가?
1.  **의미 기반 검색**: "로그인 구현 방법"과 "사용자 인증 로직"은 단어는 다르지만 의미가 유사합니다. 벡터화를 하면 이 두 문장이 
수학적으로 가깝다는 것을 인지하여 관련 정보를 찾아낼 수 있습니다.
2.  **효율적인 정보 전달**: LLM은 입력할 수 있는 텍스트 양(Context Window)에 제한이 있습니다. 수천 페이지의 문서를 통째로 넣는 대신, 
벡터 검색으로 **가장 관련 있는 2~3페이지**만 골라내어 LLM에게 전달함으로써 비용과 시간을 절약하고 정확도를 높입니다.

### 2. 추천 임베딩 모델
*   **multi-qa-mpnet-base-dot-v1**: QA(질의응답)와 검색에 특화되어 있으며, 한국어와 영어 성능이 매우 뛰어납니다. (추천 👍)
*   **bge-m3**: 최신 고성능 모델로, 검색 정확도가 매우 높습니다.
*   **nomic-embed-text**: 가볍고 범용적으로 쓰기 좋습니다.

---

## 2. 임베딩 모델 상세 가이드: multi-qa-mpnet-base-dot-v1

### 1) 임베딩 모델은 LLM(생성 모델)이 아닌가요?
네, 정확히 보셨습니다! 이 모델은 Qwen 같은 '말하는 AI'가 아니라, **'도서관 사서'** 역할을 하는 특수 모델입니다.

*   **LLM (Qwen 등)**: 정보를 읽고 문장을 작성하는 **'입'과 '뇌'** 역할.
*   **임베딩 모델**: 문장을 숫자(벡터)로 바꿔서 검색하기 좋게 만드는 **'눈'과 '인덱서'** 역할.
*   **작동 원리**: RAG를 할 때 수만 페이지 중 관련 내용을 1초 만에 찾으려면, 임베딩 모델이 미리 내용을 숫자로 지도화(Vectorizing)해놔야 합니다.

### 2) 설치 및 Open WebUI 설정 방법
Ollama를 사용 중이라면 설치와 적용이 매우 간단합니다.

1.  **터미널에서 모델 다운로드**:
    ```bash
    ollama pull multi-qa-mpnet-base-dot-v1
    ```
2.  **Open WebUI에서 모델 지정 (중요)**:
    *   `Settings(설정)` -> `Documents(문서)` 탭으로 이동합니다.
    *   `Embedding Model` 설정 항목에서 방금 받은 `multi-qa-mpnet-base-dot-v1`을 선택하고 저장하세요.
    *   이제 PDF를 업로드하거나 웹 검색을 할 때 이 모델이 '고성능 검색 엔진'으로 작동합니다.

### 3) 왜 전용 모델을 따로 써야 하나요?
*   **속도**: 거대 LLM으로 문서를 하나하나 읽으며 찾으면 하루 종일 걸리지만, 전용 모델은 순식간에 수천 개의 문서를 비교합니다.
*   **정확도**: QA와 검색에 특화되어 있어 질문의 의도와 가장 가까운 문서를 정확하게 찾아냅니다.

---

## 3. RAG의 필요성

- **최신성 유지**: LLM의 학습 데이터 이후에 나온 기술(예: 최신 Vercel SDK) 정보를 제공합니다.
- **도메인 지식 주입**: 프로젝트 내부 라이브러리나 `vercel-agent-skill` 같은 커스텀 파일의 사용법을 정확히 알게 합니다.
- **할루시네이션 방지**: 근거 문서(Source)를 바탕으로 응답하게 하여 환각 현상을 줄입니다.

---

## 4. 구현 방식 선택: Open WebUI vs AnythingLLM

로컬 RAG를 구축할 때 가장 많이 쓰이는 두 가지 도구를 비교하여 적절한 방식을 선택합니다. **현재 시스템에서는 Open WebUI를 메인으로 사용하는 것을 권장합니다.**

### 1) Open WebUI 활용 (추천 메인 본부)
채팅 인터페이스 내에서 가장 직관적으로 RAG를 활용할 수 있는 방법입니다.
*   **특징**: 채팅창에 파일 드롭, `#` 소환 기능 등으로 사용이 매우 편리합니다.
*   **상세 가이드**: **[Open WebUI RAG 및 지식 자산화 가이드](./04-1_OpenWebUI_RAG_및_지식_자산화.md)**

### 2) AnythingLLM 활용 (보조 지식 서버)
방대한 양의 문서를 영구적으로 관리하고 폴더 동기화가 필요할 때 선택합니다.
*   **특징**: 로컬 폴더 실시간 감시, 노션 스타일의 워크스페이스 관리.
*   **선택 기준**: 수천 개의 파일이나 방대한 라이브러리 전체를 모델이 항시 숙지해야 할 경우 보조적으로 사용합니다.

---

## 5. 직접 구현: Python + LangChain

프로세스를 자동화하거나 시스템에 내장하고 싶을 때 사용하는 방식입니다.

### 구현 워크플로우
1.  **Chunking**: 문서를 의미 있는 단위(함수, 페이지 등)로 자릅니다.
2.  **Embedding**: `nomic-embed-text` 같은 모델로 텍스트를 벡터(숫자)로 변환합니다.
3.  **Vector DB 저장**: FAISS나 ChromaDB에 저장합니다.
4.  **Retrieval**: 검색 쿼리와 유사한 문서 조각을 찾아 LLM 프롬프트에 주입합니다.

### 핵심 코드 예시
```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 스킬 파일 로드
loader = TextLoader("./vercel-agent-skill.js")
documents = loader.load()

# 2. 텍스트 분할 (500자 단위)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# 3. 벡터화 및 DB 저장
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = FAISS.from_documents(chunks, embeddings)

# 4. 검색 함수
def search_knowledge(query):
    docs = vector_db.similarity_search(query, k=2)
    return "\n".join([d.page_content for d in docs])
```

---

## 6. RAG 데이터 관리 전략 (데이터 결벽증 관리)

정확한 RAG 시스템을 유지하려면 '오래된 쓰레기 데이터(Garbage In)'를 철저히 배제해야 합니다. 모델이 잘못된 과거 정보를 정답으로 믿지 않게 하는 3가지 관리 전략입니다.

### 1) 버전 관리 네이밍 (파일명의 힘)
모델은 파일명을 중요한 메타데이터로 인식합니다.
*   **나쁜 예**: `code.py`, `requirement.pdf` (최신 여부 판단 불가)
*   **좋은 예**: `v1.2_final_code.py`, `2024-02-10_api_spec.md`
*   **효과**: 파일명에 날짜나 버전을 명시하면, 모델이 여러 문서를 검색했을 때 최신 파일을 우선순위로 읽을 확률이 높아집니다.

### 2) 지식 그룹화 및 호출 제어 (Collections)
방대한 데이터를 무분별하게 검색하게 두지 말고, 목적에 따라 분류하십시오.
*   **컬렉션 활용**: '프로젝트A_최신', '프로젝트A_과거기록' 등으로 분리하여 관리합니다.
*   **선별적 호출**: 채팅 시 특정 컬렉션만 지정해서 호출하면(Open WebUI의 `#` 기능 등), 과거 데이터가 존재하더라도 모델의 시야에서 원천 차단할 수 있습니다.

### 3) 정기적인 '벡터 데이터 청소' (Culling)
데이터가 수정되었다면 과거 데이터는 과감히 제거해야 합니다.
*   **Update 대신 Re-upload**: 파일을 수정했다면 기존 문서를 **삭제(Delete)**하고 새 파일을 다시 올리는 것이 가장 정확합니다. (벡터 DB 특성상 덮어쓰기보다 새로 고침의 정확도가 높습니다.)
*   **Score Threshold 상향**: 질문과 관련성이 낮은(파편화된 과거 정보) 정보가 전달되지 않도록 검색 임계값(Score Threshold)을 0.5 이상으로 상향 조절합니다.

---

## 7. 벡터화 팁

- **Chunk Size 최적화**: 너무 작으면 문맥이 끊기고, 너무 크면 관련 없는 내용이 섞입니다. 500~1000자가 적당합니다.
- **스킬 파일 주입**: `vercel-agent-skill`의 경우, 각 도구(Tool)의 설명 부분을 잘 분리하여 벡터화하면 Architect가 적절한 도구를 선택하는 능력이 비약적으로 상승합니다.
- **Ollama API 활용**: Ollama의 `format: "json"` 설정을 활용하여 검색 결과를 정형화된 데이터로 받을 수 있습니다.
