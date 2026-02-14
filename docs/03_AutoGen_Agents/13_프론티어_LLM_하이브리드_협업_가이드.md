# 13. 프론티어 LLM 하이브리드 협업 가이드 (Frontier SOS)

로컬 분산 모델(MacBook-MacMini)이 논리적 한계에 부딪히거나 극도로 복잡한 설계가 필요할 때, **Gemini 3 Flash**와 같은 클라우드 프론티어 모델에게 도움을 요청하는 '하이브리드 협업 체계'를 구축합니다.

---

## 1. 하이브리드 구조의 핵심 전략

비용 효율성과 데이터 보안을 유지하면서 결정적인 순간에만 고성능 지능을 빌려 쓰는 전략입니다.

- **로컬 처리 (90%)**:
    - MacBook(Gateway): 요청 분석 및 보안 스캔.
    - MacMini(Worker): 일상적인 코딩, 로그 분석, 단위 테스트, 기술 문서 초안 작성.
- **프론티어 요청 (10%)**:
    - 완전히 새로운 시스템의 전체 아키텍처 설계.
    - 로컬 모델이 2번 이상 해결하지 못한 고난도 버그 트래킹.
    - 최신 라이브러리(2025-2026년 이후)의 파괴적 변경사항 대응.

---

## 2. 🛡️ 분산 에이전시 운영 규칙 (Distributed Protocol)

MacBook과 MacMini가 썬더볼트로 연결된 환경에서 자원 효율을 극대화하는 규칙입니다.

### 규칙 1. [노드별 역할 고정 (Node Isolation)]
Gateway는 MacBook에서, Worker는 MacMini에서 실행하여 상호 간의 리소스 간섭을 방지합니다.
- **MacBook**: `llama3.1:8b` (Gateway) 상시 상주.
- **MacMini**: `qwen3-coder-next` (Worker) 작업 시 상주.

### 규칙 2. [체크포인트 강제 저장 (Snapshot)]
MacMini에서 모델을 전환하거나 외부 API로 위임하기 직전, 반드시 현재까지의 모든 진행 상황을 스냅샷으로 저장해야 합니다.
- **저장 항목**: `shared/temp_context.json`에 현재 구현 파일명, 직전 에러 로그, 사용자의 마지막 요구사항 기록.
- **이유**: 분산 환경에서 예기치 못한 네트워크 이슈나 모델 재로드 시 즉시 문맥을 복구하기 위함입니다.

### 규칙 3. [Frontier 위임 승인제 (Human-in-the-Loop)]
로컬 모델의 한계를 감지했을 때, 사용자의 최종 승인 단계를 거쳐 외부 API를 호출합니다.

---

## 3. 🔄 지능형 분산 워크플로우

1.  **Gateway(MacBook) 분석**: `llama3.1:8b`가 질문의 난이도 판별.
2.  **Worker(MacMini) 위임**: 분석 결과에 따라 MacMini의 `qwen3-coder-next`가 작업 수행.
3.  **한계 감지**: Worker가 작업을 완수하지 못하거나 Gateway가 고난도로 판단할 경우.
4.  **Frontier(Cloud) 요청**: 사용자의 승인 후 **Gemini 3 Flash** API 호출.
5.  **결과 피드백**: Frontier의 결과물을 MacMini의 Worker가 수령하여 로컬 환경에 맞게 코드화 및 테스트.

---

## 4. 컨텍스트 공유 전략 (Shared Storage)

분산된 노드 간에 동일한 시야를 유지하기 위한 전략입니다.

- **Shared Volume**: 썬더볼트 브릿지를 통해 `dev_repo/` 및 `shared/` 디렉토리를 두 기기가 실시간으로 공유합니다.
- **Executive Summary**: Frontier LLM 사용 시, 로컬 모델이 즉시 작업을 이어받을 수 있도록 [핵심 액션 아이템] 중심의 요약을 생성합니다.

---

## 5. 구현 방법 (router.py & Gemini API)

```python
# router.py 내 Frontier 호출 로직
if decision.use_frontier:
    # 1. 스냅샷 저장
    save_snapshot(prompt)
    
    # 2. 사용자 승인 후 Gemini 호출
    print("⚠️ 고난도 작업: Gemini 3 Flash API로 위임합니다.")
    gemini_res = await call_gemini_api(prompt)
    
    # 3. 결과물을 MacMini Worker에게 전달하여 로컬 구현
    await call_worker(gemini_res, node=MACMINI_OLLAMA)
```
