"""
TDD 자율 주행 루프 오케스트레이션

두 가지 모드:
1. Sequential: workflow.py가 직접 순서 제어 (안정적)
2. GroupChat: AutoGen GroupChat으로 에이전트 자율 대화

단일 모델 아키텍처: 모든 에이전트가 qwen3-coder-next:q4_K_M 공유.
"""

import logging
import re
import autogen

from config import (
    MAIN_LLM_CONFIG,
    GROUPCHAT_MAX_ROUND,
    MAX_TDD_RETRIES,
    MAX_REVIEW_RETRIES,
)
from agents import (
    create_planner,
    create_coder,
    create_reviewer,
    create_tester,
    create_documenter,
    create_human,
)
from tools import AgentTools

logger = logging.getLogger(__name__)


def _save_code_blocks(text: str, tools: AgentTools):
    """Coder 응답에서 파일 경로가 포함된 코드 블록을 추출하여 파일로 저장

    지원 패턴:
    1. 코드 블록 안 첫 줄: ```python\n# File: path/to/file.py\n내용```
    2. 코드 블록 바깥 윗줄: # File: path/to/file.py\n```python\n내용```
    """
    saved = {}
    ext_pattern = r"\S+\.(?:py|txt|md|cfg|toml|yaml|yml)"

    # 패턴 1: # File: path 가 코드 블록 밖(바로 윗줄)에 있는 경우
    pattern1 = rf"#\s*(?:File:\s*)({ext_pattern})\s*\n```(?:python|bash|text)?\s*\n(.*?)```"
    for filepath, content in re.findall(pattern1, text, re.DOTALL):
        saved[filepath] = content.strip()

    # 패턴 2: # File: path 가 코드 블록 안 첫 줄에 있는 경우
    pattern2 = rf"```(?:python|bash|text)?\s*\n#\s*(?:File:\s*)({ext_pattern})\s*\n(.*?)```"
    for filepath, content in re.findall(pattern2, text, re.DOTALL):
        if filepath not in saved:
            saved[filepath] = content.strip()

    for filepath, content in saved.items():
        if content:
            result = tools.write_file(filepath, content + "\n")
            logger.info(f"[SAVE] {result}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Sequential 모드 - 직접 순서 제어
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_sequential(requirement: str, tools: AgentTools) -> dict:
    """
    TDD 자율 주행 루프 (Sequential)

    흐름:
    1. Planner 설계
    2. Coder 테스트 코드 작성
    3. Coder 기능 코드 작성
    4. Tester 실행 (Docker)
    5. FAIL → Coder 수정 (최대 MAX_TDD_RETRIES회)
    6. PASS → Reviewer 검수
    7. READY_TO_COMMIT → git commit
    8. Documenter 보고서 생성
    """
    planner = create_planner()
    coder = create_coder()
    reviewer = create_reviewer()
    tester = create_tester()
    documenter = create_documenter()
    human = create_human()

    result = {
        "requirement": requirement,
        "plan": None,
        "test_result": None,
        "review_result": None,
        "report": None,
        "status": "STARTED",
    }

    # ── Step 1: 설계 ──
    logger.info("[STEP 1] Planner 설계 시작")
    plan_response = human.initiate_chat(
        planner,
        message=f"다음 요구사항을 분석하여 설계하라:\n\n{requirement}",
        max_turns=1,
    )
    result["plan"] = _extract_last_message(plan_response)
    logger.info("[STEP 1] 설계 완료")

    # ── Step 2: 코드 작성 (TDD) ──
    logger.info("[STEP 2] Coder 코드 작성 시작")
    code_response = human.initiate_chat(
        coder,
        message=(
            f"다음 설계를 바탕으로 테스트 코드와 기능 코드를 작성하라:\n\n"
            f"{result['plan']}"
        ),
        max_turns=1,
    )
    code_output = _extract_last_message(code_response)
    _save_code_blocks(code_output, tools)
    logger.info("[STEP 2] 코드 작성 완료")

    # ── Step 3-5: TDD 루프 ──
    for attempt in range(1, MAX_TDD_RETRIES + 1):
        logger.info(f"[STEP 3] 테스트 실행 (시도 {attempt}/{MAX_TDD_RETRIES})")
        test_result = tools.run_test("pytest -v")

        if test_result["exit_code"] == 0:
            logger.info("[STEP 3] 테스트 통과!")
            result["test_result"] = test_result
            break

        # exit_code 5 = no tests collected (테스트 파일 없음)
        if test_result["exit_code"] == 5:
            logger.warning("[STEP 3] 테스트 파일 없음 (exit code 5)")

        logger.info(f"[STEP 3] 테스트 실패 - Coder에게 수정 요청")
        fix_response = human.initiate_chat(
            coder,
            message=(
                f"테스트가 실패했다. 다음 로그를 분석하여 코드를 수정하라:\n\n"
                f"```\n{test_result['output'][:2000]}\n```\n\n"
                f"중요: 파일 경로를 반드시 '# File: 경로' 형식으로 코드 블록 첫 줄에 명시하라."
            ),
            max_turns=1,
        )
        code_output = _extract_last_message(fix_response)
        _save_code_blocks(code_output, tools)
    else:
        result["status"] = "TDD_FAILED"
        logger.error(f"[STEP 3] {MAX_TDD_RETRIES}회 시도 후 테스트 실패")
        return result

    # ── Step 6: 코드 리뷰 ──
    for review_attempt in range(1, MAX_REVIEW_RETRIES + 1):
        logger.info(f"[STEP 4] Reviewer 검수 (시도 {review_attempt}/{MAX_REVIEW_RETRIES})")
        review_response = human.initiate_chat(
            reviewer,
            message=f"다음 코드를 검수하라:\n\n{code_output}",
            max_turns=1,
        )
        review_output = _extract_last_message(review_response)
        result["review_result"] = review_output

        if "READY_TO_COMMIT" in review_output:
            logger.info("[STEP 4] 검수 통과 - READY_TO_COMMIT")
            break

        if "REQUEST_CHANGES" in review_output:
            logger.info("[STEP 4] 수정 요청 - Coder에게 전달")
            fix_response = human.initiate_chat(
                coder,
                message=f"Reviewer 피드백을 반영하여 수정하라:\n\n{review_output}",
                max_turns=1,
            )
            code_output = _extract_last_message(fix_response)
            _save_code_blocks(code_output, tools)

    # ── Step 7: Git 커밋 ──
    commit_result = tools.git_commit(f"feat: {requirement[:50]}")
    logger.info(f"[STEP 5] {commit_result}")

    # ── Step 8: 문서화 ──
    logger.info("[STEP 6] Documenter 보고서 생성")
    doc_response = human.initiate_chat(
        documenter,
        message=(
            f"다음 결과물을 취합하여 보고서를 작성하라:\n\n"
            f"[설계]\n{result['plan']}\n\n"
            f"[테스트 결과]\n{result['test_result']}\n\n"
            f"[리뷰 결과]\n{result['review_result']}"
        ),
        max_turns=1,
    )
    result["report"] = _extract_last_message(doc_response)
    result["status"] = "COMPLETED"
    logger.info("[DONE] Sequential 워크플로우 완료")

    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GroupChat 모드 - AutoGen 자율 대화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_groupchat(requirement: str, tools: AgentTools) -> dict:
    """
    AutoGen GroupChat으로 에이전트 자율 대화

    모든 에이전트가 대화 이력을 공유하며 자율적으로 협업.
    Tester가 ALL_TESTS_PASSED를 출력하면 종료.
    """
    planner = create_planner()
    coder = create_coder()
    reviewer = create_reviewer()
    tester = create_tester()
    human = create_human()

    groupchat = autogen.GroupChat(
        agents=[human, planner, coder, reviewer, tester],
        messages=[],
        max_round=GROUPCHAT_MAX_ROUND,
    )

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=MAIN_LLM_CONFIG,
    )

    logger.info("[GROUPCHAT] 시작")
    human.initiate_chat(
        manager,
        message=f"다음 요구사항을 TDD 방식으로 구현하라:\n\n{requirement}",
    )
    logger.info("[GROUPCHAT] 종료")

    return {
        "requirement": requirement,
        "messages": groupchat.messages,
        "status": "COMPLETED",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 유틸리티
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _extract_last_message(chat_result) -> str:
    """AutoGen ChatResult에서 마지막 메시지 텍스트 추출"""
    if hasattr(chat_result, "chat_history") and chat_result.chat_history:
        return chat_result.chat_history[-1].get("content", "")
    if hasattr(chat_result, "summary"):
        return chat_result.summary or ""
    return str(chat_result)
