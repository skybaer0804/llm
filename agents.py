"""
AutoGen 에이전트 팀 정의 (Thunderbolt 분산 아키텍처)

모든 에이전트가 Mac Mini의 qwen3-coder-next:q4_K_M을 공유.
페르소나 없이 기능적 지시사항만 부여.
CLAUDE.md 프로젝트 규칙이 모든 에이전트에 자동 주입됨.
"""

import autogen

from config import (
    MAIN_LLM_CONFIG,
    DEV_REPO,
    load_claude_rules,
    BASE_INSTRUCTION,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 공통 규칙 주입 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_combined_prompt(base_prompt: str) -> str:
    """기본 프롬프트에 CLAUDE.md 규칙을 결합"""
    rules = load_claude_rules()
    return f"{BASE_INSTRUCTION}\n{rules}\n\n[ROLE SPECIFIC INSTRUCTION]\n{base_prompt}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 기능적 지시사항 (페르소나 없음)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLANNER_INSTRUCTIONS = """요구사항을 분석하여 구현 전략과 테스트 시나리오를 정의하라.

규칙:
1. 모호한 요구사항은 추측하지 말고 'Clarification Needed'를 명시하라.
2. 극도로 복잡한 설계는 'EXTERNAL_CONSULT'를 선언하라.
3. 작업 완료 시 # SUMMARY_FOR_CODER 섹션을 생성하라.

출력 형식:
- project_structure: 생성할 파일 목록
- implementation_strategy: 구현 전략
- test_scenarios: 테스트 시나리오 목록
- external_consult_needed: true/false"""

CODER_INSTRUCTIONS = """설계서와 실패 로그를 바탕으로 코드를 작성하라.

규칙:
1. 테스트 코드를 먼저 작성하고, 그 다음 기능 코드를 작성하라.
2. 최소한의 코드로 테스트를 통과시켜라. (YAGNI 원칙)
3. 파일 경로와 전체 내용을 포함하라.
4. 설명이나 인사 없이 코드 블록만 출력하라."""

REVIEWER_INSTRUCTIONS = """코드의 가독성, 효율성, 보안 취약점을 검사하라.

보안 검수:
1. 외부 URL로의 무단 데이터 전송이 있는지 확인하라.
2. eval, exec 등 검증 없는 실행이 있는지 체크하라.
3. 민감 정보(API Key, 시스템 경로) 접근이 요구사항에 부합하는지 검토하라.

판정: 완벽하면 READY_TO_COMMIT, 수정 필요 시 REQUEST_CHANGES."""

TESTER_INSTRUCTIONS = """pytest 코드를 실행하고 결과를 분석하라.

규칙:
1. 설계서의 테스트 시나리오 조건을 모두 충족하는지 대조 검증하라.
2. 테스트 실패 시 구체적인 Traceback 분석 결과를 제공하라.
3. 환경 에러와 비즈니스 로직 에러를 구분하여 리포트하라.
4. 모든 테스트 통과 시에만 ALL_TESTS_PASSED라고 명시하라."""

DOCUMENTER_INSTRUCTIONS = """협업 결과물(설계, 코드, 테스트 결과)을 취합하여 Markdown 보고서를 작성하라.

포함 항목: 프로젝트 개요, 아키텍처, 기술 스택, 테스트 통과 지표."""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 에이전트 생성 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_planner() -> autogen.AssistantAgent:
    return autogen.AssistantAgent(
        name="Planner",
        system_message=get_combined_prompt(PLANNER_INSTRUCTIONS),
        llm_config=MAIN_LLM_CONFIG,
    )


def create_coder() -> autogen.AssistantAgent:
    return autogen.AssistantAgent(
        name="Coder",
        system_message=get_combined_prompt(CODER_INSTRUCTIONS),
        llm_config=MAIN_LLM_CONFIG,
    )


def create_reviewer() -> autogen.AssistantAgent:
    return autogen.AssistantAgent(
        name="Reviewer",
        system_message=get_combined_prompt(REVIEWER_INSTRUCTIONS),
        llm_config=MAIN_LLM_CONFIG,
    )


def create_tester() -> autogen.UserProxyAgent:
    """Tester - Docker sandbox에서 코드 실행"""
    DEV_REPO.mkdir(parents=True, exist_ok=True)
    return autogen.UserProxyAgent(
        name="Tester",
        system_message=get_combined_prompt(TESTER_INSTRUCTIONS),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        is_termination_msg=lambda x: "ALL_TESTS_PASSED" in (x.get("content", "") or ""),
        code_execution_config={
            "work_dir": str(DEV_REPO),
            "use_docker": "python:3.11-slim",
        },
        llm_config=MAIN_LLM_CONFIG,
    )


def create_documenter() -> autogen.AssistantAgent:
    return autogen.AssistantAgent(
        name="Documenter",
        system_message=get_combined_prompt(DOCUMENTER_INSTRUCTIONS),
        llm_config=MAIN_LLM_CONFIG,
    )


def create_human() -> autogen.UserProxyAgent:
    """Human Lead - 최종 승인자"""
    return autogen.UserProxyAgent(
        name="Human",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )


def create_all_agents():
    """모든 에이전트를 생성하여 dict로 반환"""
    return {
        "planner": create_planner(),
        "coder": create_coder(),
        "reviewer": create_reviewer(),
        "tester": create_tester(),
        "documenter": create_documenter(),
        "human": create_human(),
    }
