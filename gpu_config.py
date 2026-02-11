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
