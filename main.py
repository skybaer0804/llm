"""
AutoGen 멀티 에이전트 개발 시스템 - CLI 진입점

사용법:
    python main.py "파일 암호화 유틸리티를 만들어줘"
    python main.py --mode groupchat "REST API 서버 구축"
    python main.py --mode sequential "로그인 API 구현"
"""

import argparse
import logging
import sys

from config import DEV_REPO, DOCKER_IMAGE, DOCKER_NETWORK_DISABLED
from tools import AgentTools
from workflow import run_sequential, run_groupchat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent_session.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def setup_docker_container():
    """상주형 Docker 컨테이너 생성 (실패 시 None 반환)"""
    try:
        import docker

        client = docker.from_env()
        client.ping()

        container = client.containers.run(
            image=DOCKER_IMAGE,
            command="tail -f /dev/null",
            volumes={str(DEV_REPO.resolve()): {"bind": "/app", "mode": "rw"}},
            working_dir="/app",
            network_disabled=DOCKER_NETWORK_DISABLED,
            detach=True,
            auto_remove=True,
        )

        # pytest 설치
        container.exec_run("pip install pytest --quiet")
        logger.info(f"[DOCKER] 컨테이너 생성 완료: {container.short_id}")
        return container

    except ImportError:
        logger.warning("[DOCKER] docker 패키지 미설치 - subprocess 폴백")
        return None
    except Exception as e:
        logger.warning(f"[DOCKER] 컨테이너 생성 실패 - subprocess 폴백: {e}")
        return None


def cleanup_container(container):
    """컨테이너 정리"""
    if container:
        try:
            container.stop()
            logger.info("[DOCKER] 컨테이너 종료")
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="AutoGen 멀티 에이전트 TDD 개발 시스템",
    )
    parser.add_argument(
        "requirement",
        help="구현할 요구사항 (예: '파일 암호화 유틸리티를 만들어줘')",
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "groupchat"],
        default="sequential",
        help="실행 모드 (기본: sequential)",
    )
    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Docker 없이 subprocess로 테스트 실행",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("AutoGen 멀티 에이전트 TDD 개발 시스템")
    logger.info(f"모드: {args.mode}")
    logger.info(f"요구사항: {args.requirement}")
    logger.info("=" * 60)

    # Docker 컨테이너 설정
    container = None
    if not args.no_docker:
        container = setup_docker_container()

    # AgentTools 초기화
    tools = AgentTools(
        project_root=str(DEV_REPO),
        container=container,
    )

    try:
        if args.mode == "sequential":
            result = run_sequential(args.requirement, tools)
        else:
            result = run_groupchat(args.requirement, tools)

        logger.info(f"[RESULT] status={result['status']}")

        if result.get("report"):
            report_path = DEV_REPO / "REPORT.md"
            report_path.write_text(result["report"], encoding="utf-8")
            logger.info(f"[REPORT] {report_path}")

    except KeyboardInterrupt:
        logger.info("[INTERRUPTED] 사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"[ERROR] {e}", exc_info=True)
    finally:
        cleanup_container(container)


if __name__ == "__main__":
    main()
