## LLM 모델 선택 가이드

### 무료 오픈소스 모델 비교 (2026년)

| 모델 | 파라미터 / 구조 | 컨텍스트 | 멀티모달 | 코딩 | 한국어 | RAM (Q4) | tok/s | 추천용도 |
|---|---|---|---|---|---|---|---|---|
| **Llama 4 Scout** | 17B 활성 / 109B MoE | 192K (100K 권장) | 텍스트+이미지 | 상위권 | **최상** | 17GB | 30~40 | **🏆 메인 브레인**: 롱컨텍스트 + 코딩 + 한국어 |
| **Gemma3 27B** | 27B dense | 128K (실사용 32~70K 안전) | 텍스트+이미지 | 좋음 | 우수 | 17GB | 28~35 | 구글풍 멀티모달, 문서 요약·이미지 분석 |
| **Gemma3 12B** | 12B dense | 128K | 텍스트+이미지 | 보통 | 좋음 | 8GB | 40~50 | 가벼운 보조 (번역, 요약) |
| **DeepSeek-Coder V2 16B** | 16B | 64K | 텍스트 | **코딩 특화 1티어** | 보통 | 12GB | 35~45 | 🔧 **코딩 전담**: 리팩터링, 테스트, 설계 |
| **Qwen2.5 32B** | 32B dense | 32~64K | 텍스트(일부 비전) | 상위권 | **다국어 최고** | 19GB | 20~30 | 한글 주석 + 코드, 번역 강점 |
| **Qwen2.5 72B** | 72B dense | 32~64K | 텍스트 | 상위권 | 최고 | 42GB | 12~18 | 무거운 추론 작업용 (M4 Pro: 제한적) |
| **GPT-OSS 20B** | 20B dense | 32K | 텍스트 | 우수 | 우수 | 12GB | 25~35 | OpenAI 스타일, Flash API 대체용 |
| **GPT-OSS 120B** | 120B dense | 32K | 텍스트 | **최고급** | 최고 | 75GB | 불가(M4) | 서버급 (M4 Pro 용량 초과) |
| **Gemini 3 Flash** (클라우드) | 비공개 Frontier급 | **1M 토큰** | 텍스트+이미지+오디오+비디오 | Frontier급 | 상위권 | API만 | 200+ tok/s | 💎 **Final Boss**: 초장문·최고 품질 (유료) |

### 추천 구성 (M4 Pro 64GB 기준)

**기본 설정 (무료, 전기세만)**
```
메인 3개 모델:
1. Llama 4 Scout (17GB) → 메인 브레인
2. Gemma3 12B (8GB) → 보조 멀티모달  
3. DeepSeek-Coder V2 16B (12GB) → 코딩 전담
합계: 37GB (여유 27GB)

설치:
ollama pull llama4:scout-q4_K_M
ollama pull gemma3:12b
ollama pull deepseek-coder-v2:16b
```

**옵션 (품질 최우선)**
```
1. Llama 4 Scout (17GB)
2. Gemma3 27B (17GB)  
3. DeepSeek-Coder V2 16B (12GB)
합계: 46GB (여유 18GB)
```

**극한 구성 (한국어 + 코딩 최강)**
```
1. Llama 4 Scout (17GB)
2. Qwen2.5 32B (19GB)
3. DeepSeek-Coder V2 16B (12GB)
합계: 48GB (여유 16GB)
```