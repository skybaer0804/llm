# 01. 듀얼 맥 & Git 기반 하이브리드 에이전트 아키텍처

맥미니(Mac Mini)의 로컬 멀티 에이전트와 맥북(MacBook)의 Claude Code를 썬더볼트 및 Git으로 연결하여, 보안과 비용 효율성을 극대화한 **"하이브리드 듀얼 브레인"** 시스템의 구축 가이드입니다.

---

## 1. 아키텍처 개요: 두뇌의 역할 분담

이 시스템은 물리적으로 분리된 두 기기를 하나의 유기적인 지능형 시스템으로 통합합니다.

*   **맥미니 (Architect & Planner)**: "로컬 사령관"
    *   **역할**: 인터넷 검색, 전체 설계, 작업 분할(Tasking), 결과 검증(Testing).
    *   **장점**: 로컬 LLM(Ollama) 사용으로 비용 "0", 데이터 유출 없음.
*   **맥북 (Executor & Coder)**: "고지능 실행가"
    *   **역할**: 맥미니가 지시한 `Task`를 수행, 고난이도 코딩, 리팩토링.
    *   **장점**: Claude Code(Plan 요금제)를 활용하여 API 키 없이 고성능 추론 수행.

---

## 2. 연결 및 통신 프로토콜

### 2.1 물리적 연결 (썬더볼트 브릿지)
두 기기를 썬더볼트 케이블로 직접 연결하여 인터넷을 거치지 않는 초고속 로컬 네트워크(IP over Thunderbolt)를 구성합니다.
*   **속도**: 10Gbps ~ 20Gbps (대용량 파일/Git 리포지토리 즉시 동기화)
*   **보안**: 외부 네트워크와 분리된 폐쇄망 통신 가능.

### 2.2 공유 메모리 (Git & SMB)
Git 리포지토리를 단순 소스 저장소가 아닌 **"공유 기억장치(Shared Memory)"**로 활용합니다. 듀얼 맥 환경의 복잡성을 최소화하기 위해 별도의 DB(SQLite 등) 없이 파일 시스템과 Git 로그만으로 상태를 관리합니다.

1.  **SMB 마운트**: 맥북의 프로젝트 폴더를 맥미니에 마운트하여 실시간 접근.
2.  **파일 기반 상태 관리**:
    *   **`Task.md`**: 맥미니가 작성하는 구체적인 작업 지시서.
    *   **`issues/issue-{ID}/status.json`**: 각 이슈의 처리 상태(Queue, Analysis, Execution, Hold, Completed) 기록.
    *   **Git Commit History**: 에이전트가 수행한 모든 변경 사항의 영구적 기록.
    *   **GitHub Issues/PRs**: 라벨과 댓글을 실시간 운영 상태 저장소로 활용.
    *   **`SYSTEM_PAUSE.lock`**: Claude Code 쿼터 제한 시 생성되는 일시 정지 신호.

---

## 3. 워크플로우: 기획부터 실행까지

### 단계 1: 설계 및 분할 (Mac Mini)
맥미니의 **Architect 에이전트**가 사용자 요청을 분석하고, 이를 실행 가능한 단위로 쪼갭니다.
*   **Atomic Task 원칙**:
    *   입/출력(I/O)이 명확해야 함.
    *   수정 파일은 3~5개 이내로 제한.
    *   **검증 가능성(Testable)**: "성공 기준"이 명시되어야 함.
*   **산출물**: `tasks/pending/Task-01.md` 생성.

### 단계 2: 작업 지시 (Handshake)
맥미니가 맥북에게 작업을 요청합니다.
*   **SSH Trigger**: 맥미니에서 스크립트로 맥북의 Claude Code를 원격 실행.
    ```bash
    ssh macbook "cd ~/project && claude-code 'read tasks/pending/Task-01.md and implement it'"
    ```

### 단계 3: 고지능 실행 (MacBook)
맥북의 **Claude Code**가 지시서를 읽고 코드를 작성합니다.
*   **Branch**: `execution/task-01` 브랜치 생성 후 작업.
*   **Self-Correction**: Claude Code가 자체적으로 코드를 수정하고 1차 테스트 수행.
*   **완료**: 작업 결과를 `main` 또는 `feature` 브랜치에 푸시하고 `Task-01.md`를 `tasks/done/`으로 이동.

### 단계 4: 검증 및 피드백 (Mac Mini)
맥미니의 **Reviewer 에이전트**가 결과를 검증합니다.
*   **Role Change**: 코드를 눈으로 읽는 것이 아니라, **실제로 실행**해봅니다.
*   **Pass**: 통합 테스트 통과 시 최종 승인.
*   **Fail**: 에러 로그(`error.log`)를 첨부하여 다시 맥북에게 수정 요청 (Re-assign).

---

## 4. 장애 대응 및 쿼터 관리 전략

Claude Code의 사용량 제한(Rate Limit)이나 일시적 오류 발생 시 시스템이 멈추지 않도록 유연하게 대처합니다.

### 4.1 일시적 제한 (Sliding Quota) -> "Hold & Wait"
Claude Code가 "Rate limit reached" 오류를 반환할 경우:
1.  **Lock**: `SYSTEM_PAUSE.lock` 파일 생성 (재개 예정 시간 기록).
2.  **Hold**: 맥미니는 대기 모드로 전환하고 사용자에게 알림.
3.  **Resume**: 예정 시간이 되면 자동으로 락을 해제하고 작업 재개 요청.

### 4.2 완전 소진 (Exhausted) -> "Fallback"
시간이 지나도 해결되지 않거나 쿼터가 완전 소진된 경우:
1.  **Fallback**: 맥미니의 로컬 LLM(Codestral, Qwen 등)이 긴급 수정 수행.
2.  **Handover**: 사용자에게 현재 상태(`git diff`)를 리포트하고 수동 개입 요청.

---

## 5. 파일 구조 예시

```text
project_root/
├── .git/
├── docs/               # 설계 문서 (Architect)
├── tasks/              # 작업 지시서 (Shared Memory)
│   ├── pending/        # 대기 중인 작업
│   └── done/           # 완료된 작업
├── AGENT_STATUS.json   # 에이전트 상태 공유
├── SYSTEM_PAUSE.lock   # 일시 정지 플래그 (존재 시 대기)
└── src/                # 소스 코드
```

---

> **💡 핵심 요약**: 맥미니는 "두뇌(기획)"와 "손발(검증)", 맥북은 "천재적인 직관(코딩)"을 담당합니다. Git은 이 둘을 이어주는 "신경망"입니다.
