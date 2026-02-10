# 06. Local Executor 보안 및 샌드박스 설정

로컬 LLM이 생성한 코드를 호스트 환경에서 직접 실행하는 것은 매우 위험합니다. 에이전트의 실수나 할루시네이션으로 인해 시스템이 파손되는 것을 방지하기 위해 격리된 환경(Sandbox)에서 코드를 실행하는 보안 설정이 필수적입니다.

## 1. 코드 실행 보안의 필요성

LLM은 다음과 같은 위험한 코드를 생성할 가능성이 있습니다:
- **시스템 파괴**: `rm -rf /`와 같은 명령어 실행.
- **설정 변경**: 시스템 환경 설정이나 보안 옵션 수정.
- **데이터 유출**: 개인 파일이나 환경 변수(.env) 접근 및 외부 전송.

이러한 위험을 차단하기 위해 **격리된 샌드박스(Sandbox)** 환경을 구축해야 합니다.

## 2. 샌드박스 구현 전략

### 2.1 상주형 컨테이너 전략 (Persistent Sandbox - 권장)

매번 컨테이너를 생성하는 오버헤드를 줄이고, 로컬 Git 저장소의 파일을 실시간으로 검증하기 위해 **"로컬 디렉토리 바인딩"**과 **"상주형 컨테이너"** 방식을 결합합니다.

**핵심 전략:**
- **하나의 컨테이너**: 에이전시 세션 시작 시 컨테이너를 하나만 띄우고 계속 재사용합니다.
- **볼륨 바인딩**: 호스트의 프로젝트 폴더를 컨테이너의 `/app`에 연결하여 파일 변경사항을 즉시 공유합니다.
- **고속 명령 실행**: `docker exec` 명령을 통해 이미 실행 중인 컨테이너에 명령만 전달하므로 지연 시간(Latency)이 0.5초 내외로 매우 짧습니다.

```python
import docker
import os

client = docker.from_env()

# 프로젝트 절대 경로
project_path = os.path.abspath("./my-project")

# 1. 에이전시 시작 시 상주형 컨테이너 실행
container = client.containers.run(
    image="python:3.11-slim",
    command="tail -f /dev/null",  # 컨테이너 유지용 대기 명령
    volumes={project_path: {'bind': '/app', 'mode': 'rw'}},
    working_dir="/app",
    network_disabled=True,
    detach=True
)

def run_test_in_sandbox(command="pytest"):
    """상주 중인 컨테이너에서 테스트 명령 실행"""
    # 컨테이너를 껐다 켜는 게 아니라 'exec_run'으로 명령만 전달 (매우 빠름)
    exit_code, output = container.exec_run(command)
    return {
        "status": "PASS" if exit_code == 0 else "FAIL",
        "log": output.decode('utf-8')
    }

# 2. 세션 종료 시 컨테이너 중지
# container.stop()
```

### 2.2 Python 리소스 제한 (Subprocess 활용)

Docker 사용이 불가능한 경우, 최소한 파이썬 수준에서 실행 시간과 권한을 강하게 제한해야 합니다.

**핵심 제한 사항:**
- **Timeout**: 무한 루프 방지를 위해 일정 시간(예: 5초) 후 강제 종료.
- **Non-Root**: 루트 권한이 아닌 별도의 제한된 사용자 계정으로 실행.

```python
import subprocess

try:
    result = subprocess.run(
        ["python3", "temp_code.py"],
        capture_output=True,
        text=True,
        timeout=5,  # 5초 초과 시 강제 종료
        check=True
    )
except subprocess.TimeoutExpired:
    print("❌ 보안 위험: 실행 시간이 너무 길어 중단되었습니다.")
except subprocess.CalledProcessError as e:
    print(f"❌ 실행 에러: {e.stderr}")
```

## 3. 필수 보안 체크리스트 (Security Audit)

코드를 실행하기 전, 중계자(Router)나 리뷰어(Reviewer) 에이전트가 위험 요소를 먼저 검사하도록 프로세스를 설계합니다.

1.  **금지 키워드 필터링**: `os.remove`, `shutil.rmtree`, `subprocess.run`, `socket`, `eval`, `exec` 등 시스템 영향을 주는 함수 포함 여부 확인.
2.  **접근 제한**: 코드가 읽고 쓸 수 있는 공간을 특정 프로젝트 폴더 내(`/tmp/sandbox`)로 한정하고, 부모 디렉토리(`..`) 접근을 차단합니다.
3.  **정적 분석**: 실행 전 추상 구문 트리(AST) 분석을 통해 위험한 호출을 사전에 차단합니다.

## 4. M4 Pro 환경에서의 이점

Mac mini M4 Pro는 **가상화 및 I/O 성능**이 매우 뛰어납니다. 
- **초고속 명령 실행**: 상주형 컨테이너와 `exec_run` 조합은 지연 시간이 거의 없어, 수십 번의 TDD 루프를 돌아도 쾌적한 개발 환경을 제공합니다.
- **효율적 볼륨 동기화**: 강력한 CPU와 빠른 SSD 덕분에 호스트와 컨테이너 간의 파일 동기화(Volume Binding) 시 성능 저하가 없습니다.
- **안정적인 다중 세션**: 64GB의 메모리를 활용해 여러 프로젝트의 샌드박스를 동시에 띄워도 시스템 부하가 매우 적습니다.

## 5. 결론

단순히 `exec()`나 `eval()`을 사용하는 것은 절대 금물입니다. 최소한 **Docker**를 연동하거나, **Subprocess의 Timeout** 설정을 반드시 적용하여 내 소중한 시스템을 LLM의 잠재적 실수로부터 보호해야 합니다.
