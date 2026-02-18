"""
에이전트 전용 툴 (Agent Tools)

에이전트가 호스트 파일 시스템과 Docker 샌드박스를 조작하기 위한 인터페이스.
보안: 경로 탈출 방지, 명령어 화이트리스트, AST 기반 사전 검사.
"""

import ast
import os
import subprocess
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# 실행 허용 명령어 화이트리스트
ALLOWED_COMMANDS = {"pytest", "python", "pylint", "black", "pip"}

# AST 보안 검사 대상 (위험 함수/모듈)
DANGEROUS_CALLS = {
    "eval", "exec", "compile", "__import__",
    "os.system", "os.popen", "os.remove", "os.rmdir",
    "subprocess.run", "subprocess.call", "subprocess.Popen",
    "shutil.rmtree",
}

DANGEROUS_IMPORTS = {"socket", "http.client", "urllib.request", "ftplib", "smtplib"}


class AgentTools:
    """에이전트가 사용하는 파일 I/O, 테스트 실행, Git 커밋 도구"""

    def __init__(self, project_root: str, container=None):
        """
        Args:
            project_root: 호스트의 프로젝트 절대 경로 (dev_repo)
            container: Docker 컨테이너 객체 (None이면 subprocess 폴백)
        """
        self.root = Path(project_root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.container = container

    # ── 파일 I/O ──

    def write_file(self, path: str, content: str) -> str:
        """프로젝트 디렉토리 내 파일 쓰기 (경로 탈출 방지)"""
        full_path = (self.root / path).resolve()
        if not str(full_path).startswith(str(self.root)):
            return f"SECURITY_ERROR: 경로 탈출 시도 차단 - {path}"

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        logger.info(f"[TOOL] write_file: {path}")
        return f"OK: {path} 저장 완료 ({len(content)} bytes)"

    def read_file(self, path: str) -> str:
        """프로젝트 디렉토리 내 파일 읽기"""
        full_path = (self.root / path).resolve()
        if not str(full_path).startswith(str(self.root)):
            return f"SECURITY_ERROR: 경로 탈출 시도 차단 - {path}"

        if not full_path.exists():
            return f"ERROR: 파일 없음 - {path}"

        return full_path.read_text(encoding="utf-8")

    def list_files(self, directory: str = ".") -> list:
        """프로젝트 디렉토리 내 파일 목록"""
        target = (self.root / directory).resolve()
        if not str(target).startswith(str(self.root)):
            return []

        if not target.is_dir():
            return []

        return [
            str(p.relative_to(self.root))
            for p in target.rglob("*")
            if p.is_file() and "__pycache__" not in str(p)
        ]

    # ── 테스트 실행 ──

    def run_test(self, command: str = "pytest") -> Dict[str, Any]:
        """샌드박스에서 테스트 실행 (Docker 우선, subprocess 폴백)"""
        base_cmd = command.split()[0]
        if base_cmd not in ALLOWED_COMMANDS:
            return {
                "exit_code": -1,
                "output": f"SECURITY_ERROR: 허용되지 않은 명령어 - {base_cmd}",
            }

        if self.container:
            return self._run_in_docker(command)
        return self._run_in_subprocess(command)

    def _run_in_docker(self, command: str) -> Dict[str, Any]:
        """Docker 컨테이너에서 실행"""
        try:
            exit_code, output = self.container.exec_run(
                command, workdir="/app"
            )
            return {
                "exit_code": exit_code,
                "output": output.decode("utf-8", errors="replace"),
            }
        except Exception as e:
            logger.error(f"[TOOL] Docker exec 실패: {e}")
            return {"exit_code": -1, "output": f"DOCKER_ERROR: {e}"}

    def _run_in_subprocess(self, command: str) -> Dict[str, Any]:
        """subprocess 폴백 (Docker 없을 때, timeout 30초)"""
        try:
            # venv 내 python -m 으로 실행하여 PATH 문제 방지
            parts = command.split()
            if parts[0] in ("pytest", "pylint", "black"):
                parts = [sys.executable, "-m"] + parts

            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.root),
            )
            return {
                "exit_code": result.returncode,
                "output": result.stdout + result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "output": "TIMEOUT: 실행 시간 초과 (30초)"}
        except Exception as e:
            return {"exit_code": -1, "output": f"EXEC_ERROR: {e}"}

    # ── Git ──

    def git_commit(self, message: str) -> str:
        """테스트 성공 시 자동 커밋"""
        try:
            subprocess.run(
                ["git", "-C", str(self.root), "add", "."],
                check=True, capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(self.root), "commit", "-m", message],
                check=True, capture_output=True,
            )
            logger.info(f"[TOOL] git_commit: {message}")
            return f"OK: 커밋 완료 - {message}"
        except subprocess.CalledProcessError as e:
            return f"GIT_ERROR: {e.stderr.decode('utf-8', errors='replace')}"

    # ── 보안 검사 ──

    @staticmethod
    def security_check(code: str) -> Dict[str, Any]:
        """AST 기반 보안 사전 검사"""
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"safe": False, "issues": [f"구문 오류: {e}"]}

        for node in ast.walk(tree):
            # 위험 함수 호출 검사
            if isinstance(node, ast.Call):
                func_name = _get_call_name(node)
                if func_name in DANGEROUS_CALLS:
                    issues.append(
                        f"위험 호출: {func_name} (line {node.lineno})"
                    )

            # 위험 모듈 import 검사
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in DANGEROUS_IMPORTS:
                        issues.append(
                            f"위험 import: {alias.name} (line {node.lineno})"
                        )
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module in DANGEROUS_IMPORTS:
                    issues.append(
                        f"위험 import: {node.module} (line {node.lineno})"
                    )

        return {"safe": len(issues) == 0, "issues": issues}


def _get_call_name(node: ast.Call) -> str:
    """AST Call 노드에서 함수명 추출"""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            return f"{node.func.value.id}.{node.func.attr}"
    return ""
