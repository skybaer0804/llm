# 02. Docker 및 보안 설정

OpenWebUI 운영 및 격리된 실행 환경을 위해 Docker를 설치하고, 로컬 서버의 안전한 접근을 위한 보안 설정을 수행합니다.

## 1. Docker Desktop 설치

1. [Docker 공식 홈페이지](https://www.docker.com/products/docker-desktop/)에서 **Apple Silicon** 버전을 다운로드합니다.
2. DMG 파일을 실행하여 `Docker` 아이콘을 `Applications` 폴더로 드래그합니다.
3. `Applications`에서 Docker를 실행하고 권한 허용을 완료합니다.

> **💡 에이전트 보안과 Docker**: AutoGen의 `Tester_QA` 에이전트는 작성된 코드를 실제 실행하여 검증합니다. 이때 Docker는 로컬 시스템과 분리된 **격리된 실행 환경(Sandbox)**을 제공하여, 혹시 모를 악성 코드나 프롬프트 주입 공격으로부터 호스트 OS를 보호하는 핵심 보안 장치 역할을 합니다.

### 자동 시작 설정
Docker Desktop 설정(톱니바퀴 아이콘) → **General** → **Start Docker Desktop when you log in** 체크를 권장합니다.

## 2. 보안 설정 및 원격 접근

로컬 LLM 서버를 안전하게 보호하면서 필요시 외부에서 접근하는 방법입니다.

### OpenWebUI 로컬 바인딩 (기본 보안)
기본적으로 외부에서 직접 접근할 수 없도록 `127.0.0.1`에만 포트를 바인딩합니다.
```bash
docker run -d \
  -p 127.0.0.1:3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### 안전한 원격 접근 (VPN 활용)
공용 인터넷에 포트를 열지 않고 안전하게 접속하는 방법입니다.

- **Tailscale (권장)**: 설정이 가장 간편하며 무료로 기기 간 전용망을 구축합니다.
  ```bash
  brew install tailscale
  tailscale up
  ```
- **Cloudflare Tunnel**: 도메인을 통해 안전하게 터널링합니다.
  ```bash
  brew install cloudflare/cloudflare/cloudflared
  cloudflared tunnel --url http://localhost:3000
  ```

## 3. Docker 실행 권한 (CLI)
터미널에서 `sudo` 없이 docker 명령어를 사용하기 위한 설정입니다.
```bash
# 일반 사용자에게 권한 부여
sudo usermod -aG docker $USER
# 적용을 위해 로그아웃 후 다시 로그인하거나 아래 명령 실행
newgrp docker
```
*참고: macOS에서는 Docker Desktop 설치 시 자동으로 권한이 관리되므로 위 과정이 생략될 수 있습니다.*
