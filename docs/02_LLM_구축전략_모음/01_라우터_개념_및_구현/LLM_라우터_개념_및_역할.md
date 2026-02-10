# LLM 라우터 개념 및 역할

## 🎯 개요

이 `router.py`는 다음 역할을 수행합니다:

1.  **작업 분류 (Task Classification)**  
    GitHub 이슈 / AutoGen 요청 → 역할 판단 (설계 / 코딩 / 검수)

2.  **LLM 라우팅**  
    *   설계/분석 → `qwen3-coder-next:q4_K_M` (52GB, Planner)
    *   코딩 구현 → `qwen3-coder:32b` (19GB, Dev1)
    *   검수/테스트 → `qwen3:14b` (9GB, Dev2/Tester)

3.  **메모리 관리**  
    *   메모리 체크 후 필요시 이전 모델 언로드
    *   순차 실행 강제 (동시 2개 모델까지만 허용)

4.  **헬스 체크 & 모니터링**  
    *   Ollama 서버 상태 체크
    *   모델 로드/언로드 로깅
    *   응답 시간 측정

## 📊 라우팅 규칙 정리

| Task Type    | 모델             | 에이전트  | 용도         |
| :----------- | :--------------- | :-------- | :----------- |
| `plan`       | Qwen3-Coder-Next | Architect | 계획 수립    |
| `design`     | Qwen3-Coder-Next | Architect | 아키텍처 설계 |
| `architecture` | Qwen3-Coder-Next | Architect | 시스템 설계   |
| `requirements` | Qwen3-Coder-Next | Architect | 요구사항 분석 |
| `strategy`   | Qwen3-Coder-Next | Architect | 전략 수립    |
| `code`       | Qwen3-Coder 32B  | Coder     | 코딩         |
| `implement`  | Qwen3-Coder 32B  | Coder     | 구현         |
| `refactor`   | Qwen3-Coder 32B  | Coder     | 리팩터링     |
| `fix`        | Qwen3-Coder 32B  | Coder     | 버그 수정    |
| `feature`    | Qwen3-Coder 32B  | Coder     | 기능 추가    |
| `optimize`   | Qwen3-Coder 32B  | Coder     | 최적화       |
| `review`     | Qwen3 14B        | Reviewer  | 코드 리뷰    |
| `test`       | Qwen3 14B        | Reviewer  | 테스트 작성  |
| `qa`         | Qwen3 14B        | Reviewer  | QA           |
| `validate`   | Qwen3 14B        | Reviewer  | 검증         |
| `debug`      | Qwen3 14B        | Reviewer  | 디버깅       |
| `summary`    | Qwen3 14B        | Reviewer  | 요약         |

## ⚙️ 메모리 관리 전략

### 순차 실행 (Sequential)

```
시간 →

[요청 1] Architect (설계) - 52GB 사용, 3-5분
메모리 해제
[요청 2] Coder (구현) - 19GB 사용, 5-10분
메모리 해제
[요청 3] Reviewer (검수) - 9GB 사용, 2-3분
```

이 라우터가 **자동으로** 이 순서를 관리합니다.

### 병렬 실행 (Parallel, 제한적)

```
[Coder 19GB] + [Reviewer 9GB] = 28GB
→ 동시 실행 가능 (64GB 시스템에서 여유)

단, Architect는 절대 다른 모델과 동시 X
```