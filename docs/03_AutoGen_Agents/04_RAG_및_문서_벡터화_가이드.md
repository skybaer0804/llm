# 04. RAG 및 문서 벡터화 가이드

에이전트가 최신 라이브러리 용법이나 프로젝트 전용 스킬(`vercel-agent-skill`)을 정확히 이해하게 하려면 **RAG(Retrieval-Augmented Generation)** 시스템 구축이 필수적입니다.

---

## 1. 벡터화(Vectorization)란?

### 벡터화란?
텍스트(언어)를 컴퓨터가 수학적으로 연산할 수 있는 **숫자 배열(Vector)**로 변환하는 과정을 말합니다. 단순한 키워드 매칭이 아니라 문장의 '의미'를 숫자로 수치화하는 것이 핵심입니다.

### 왜 하는가?
1.  **의미 기반 검색**: "로그인 구현 방법"과 "사용자 인증 로직"은 단어는 다르지만 의미가 유사합니다. 벡터화를 하면 이 두 문장이 수학적으로 가깝다는 것을 인지하여 관련 정보를 찾아낼 수 있습니다.
2.  **효율적인 정보 전달**: LLM은 입력할 수 있는 텍스트 양(Context Window)에 제한이 있습니다. 수천 페이지의 문서를 통째로 넣는 대신, 벡터 검색으로 **가장 관련 있는 2~3페이지**만 골라내어 LLM에게 전달함으로써 비용과 시간을 절약하고 정확도를 높입니다.

---

## 2. RAG의 필요성

- **최신성 유지**: LLM의 학습 데이터 이후에 나온 기술(예: 최신 Vercel SDK) 정보를 제공합니다.
- **도메인 지식 주입**: 프로젝트 내부 라이브러리나 `vercel-agent-skill` 같은 커스텀 파일의 사용법을 정확히 알게 합니다.
- **할루시네이션 방지**: 근거 문서(Source)를 바탕으로 응답하게 하여 환각 현상을 줄입니다.

---

## 3. 간편 구현: AnythingLLM 활용

GUI를 통해 별도의 코딩 없이 가장 쉽게 RAG를 구축하는 방법입니다.

1.  **설치**: [AnythingLLM Desktop](https://useanything.com/)을 설치합니다.
2.  **임베딩 모델 설정**: 설정에서 `nomic-embed-text` (Ollama)를 선택합니다.
3.  **워크스페이스 생성**: 프로젝트별 워크스페이스를 만듭니다.
4.  **문서 업로드**: `vercel-agent-skill.js` 파일이나 관련 공식 문서(PDF, MD)를 드래그 앤 드롭합니다.
5.  **API 연동**: 에이전트가 질문할 때 AnythingLLM의 API를 통해 관련 내용을 검색하여 프롬프트에 합쳐줍니다.

---

## 4. 직접 구현: Python + LangChain

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

## 5. 벡터화 팁

- **Chunk Size 최적화**: 너무 작으면 문맥이 끊기고, 너무 크면 관련 없는 내용이 섞입니다. 500~1000자가 적당합니다.
- **스킬 파일 주입**: `vercel-agent-skill`의 경우, 각 도구(Tool)의 설명 부분을 잘 분리하여 벡터화하면 Architect가 적절한 도구를 선택하는 능력이 비약적으로 상승합니다.
- **Ollama API 활용**: Ollama의 `format: "json"` 설정을 활용하여 검색 결과를 정형화된 데이터로 받을 수 있습니다.
