# 00. macOS 시스템 최적화 (GPU 메모리 확장)

Mac M4 Pro 64GB 환경에서 `qwen3-coder-next:q4_K_M` (약 52GB)와 같은 대형 모델을 원활하게 구동하기 위해서는 macOS의 기본 GPU 메모리 할당 제한을 해제해야 합니다.

## 1. GPU 메모리 제한 해제 필요성

macOS는 기본적으로 시스템 전체 메모리(Unified Memory)의 약 70~80% 이상을 GPU가 점유하지 못하도록 제한합니다. 64GB 모델의 경우 기본적으로 약 44.8GB(70%) 내외가 한계이며, 이 경우 52GB 모델 로드 시 메모리 부족으로 인한 스왑 발생 및 성능 저하가 일어납니다. 이를 방지하기 위해 한계를 **56GB(약 87%)**까지 수동으로 확장해야 합니다.

## 2. 터미널 명령어 (즉시 적용)

아래 명령어를 터미널에 입력하면 즉시 GPU 할당 제한이 56GB로 확장됩니다. (비밀번호 입력 필요)

```bash
# 56GB 설정 (56 * 1024 = 57344MB)
sudo sysctl iogpu.wired_limit_mb=57344
```

*참고: 이 설정은 시스템 재부팅 시 초기값으로 초기화됩니다.*

## 3. 재부팅 시 자동 적용을 위한 Python 스크립트

시스템이 재시작될 때마다 수동으로 설정하는 번거로움을 피하기 위해, 프로젝트 실행 시 자동으로 최적화를 수행하는 Python 코드를 작성합니다.

### 3.1. 최적화 스크립트 (`src/utils/mac_optimize.py`)

```python
import subprocess
import os
import sys

def optimize_gpu_memory(limit_gb=56):
    """
    macOS의 GPU Wired Memory 제한을 확장합니다.
    (M1/M2/M3/M4 Apple Silicon Mac 전용)
    """
    if sys.platform != "darwin":
        return

    limit_mb = limit_gb * 1024
    
    # 현재 설정된 제한값 확인
    try:
        current_limit = subprocess.check_output(["sysctl", "-n", "iogpu.wired_limit_mb"]).decode().strip()
        if current_limit == str(limit_mb):
            print(f"[✅] GPU Memory Limit is already set to {limit_gb}GB.")
            return
    except Exception:
        pass

    print(f"[⚙️] Setting GPU Memory Limit to {limit_gb}GB (Password required)...")
    
    # sudo 권한으로 sysctl 명령어 실행
    # os.system을 사용하여 터미널의 비밀번호 입력 프롬프트를 활용합니다.
    cmd = f"sudo sysctl iogpu.wired_limit_mb={limit_mb}"
    result = os.system(cmd)
    
    if result == 0:
        print(f"[🚀] Successfully optimized GPU memory for M4 Pro.")
    else:
        print(f"[❌] Failed to set GPU memory limit. Please run manually.")

if __name__ == "__main__":
    optimize_gpu_memory()
```

### 3.2. 실행 위치 및 연동 가이드

이 스크립트는 프로젝트의 메인 진입점이나 환경 설정 단계에서 가장 먼저 실행되어야 합니다.

1.  **실행 위치**: `src/utils/mac_optimize.py` 경로에 파일을 저장합니다.
2.  **연동 방법**: AutoGen을 실행하는 `main.py` 또는 `entrypoint.py` 파일 최상단에서 해당 함수를 호출합니다.

```python
# main.py 또는 entrypoint.py
from src.utils.mac_optimize import optimize_gpu_memory

# [Step 0] GPU 메모리 최적화 (가장 먼저 실행)
optimize_gpu_memory(56)

# [Step 1] 이후 에이전트 및 모델 로드 로직 진행
# ...
```

---
*주의: `sudo` 명령이 포함되어 있어 최초 실행 시 1회 비밀번호 입력이 필요할 수 있습니다. 무인 환경에서 실행하려면 `/etc/sudoers` 설정을 통한 NOPASSWD 권한 부여가 필요합니다.*
