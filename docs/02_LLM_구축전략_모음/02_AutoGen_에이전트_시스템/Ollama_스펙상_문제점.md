## 2. Ollama 실제 스펙 기준으로 본 문제점

문제는 **Ollama에 올라와 있는 Qwen3-Coder-Next의 실제 모델 구조/사이즈**입니다.

### 2-1. Ollama에 있는 Qwen3-Coder-Next 라인업

Ollama `qwen3-coder-next` 페이지 기준으로 현재 모델은 다음 네 개뿐입니다.[^2_2]

- `qwen3-coder-next:latest` – 52GB, 256K context
- `qwen3-coder-next:cloud` – (클라우드 프록시 용, 용량 표기 없음)
- `qwen3-coder-next:q4_K_M` – 52GB, 256K context
- `qwen3-coder-next:q8_0` – 85GB, 256K context

즉,

- **7B / 14B / 32B 같은 “사이즈가 다른 Qwen3-Coder-Next”는 Ollama 라이브러리에는 없습니다.**
- 지금은 **하나의 80B MoE 모델을 다른 양자화(q4_K_M, q8_0)로만 제공**하는 구조입니다.[^2_1][^2_2]

말씀하신

> qwen3-coder-next:32b-q4_K_M
> qwen3-coder-next:14b-q8_0
> qwen3-coder-next:7b-q8_0

같은 태그는 **Ollama 공식 태그 체계에는 존재하지 않는 조합**입니다.
(직접 GGUF 만들어서 로컬로 로드하면야 뭐든 할 수 있지만, “ollama pull …” 수준에서는 안 됩니다.)

### 2-2. 메모리 추정이 실제보다 훨씬 작게 잡혀 있음

Ollama 기준 용량은:

- `qwen3-coder-next:q4_K_M` → **52GB**
- `qwen3-coder-next:q8_0` → **85GB**[^2_3][^2_2]

이고, Unsloth 문서도 **4비트 기준 46GB 정도 메모리 필요**라고 안내합니다.[^2_1]

따라서:

- 32B-q4_K_M ≈ 20GB
- 14B-q8_0 ≈ 15GB
- 7B-q8_0 ≈ 8GB

이런 숫자는 **일반 dense Qwen3 32B/14B/7B 계열에 더 가깝고**,
Qwen3-Coder-Next(80B MoE)의 Ollama 실제 용량과는 맞지 않습니다.[^2_4][^2_2]

그리고 M4 Pro 64GB 기준으로 보면:

- `qwen3-coder-next:q8_0` (85GB)는 **아예 안 들어갑니다**. (RAM < 모델 사이즈)[^2_2][^2_1]
- `qwen3-coder-next:q4_K_M`(52GB)는 **한 개만 단독으로 돌리는 건 가능하지만**,
macOS + 기타 프로세스까지 고려하면 여유가 아주 많지는 않습니다.

즉, **지금처럼 Qwen3-Coder-Next를 3개 인스턴스로 동시에 띄워서 각기 Architect / Coder / Reviewer로 쓰는 구조는 64GB 환경에서는 불가능**합니다.