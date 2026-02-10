## Docker 설치 및 설정

### Docker Desktop 설치 (Mac M4)

1. https://www.docker.com/products/docker-desktop/ 에서 Apple Silicon 버전 다운로드
2. DMG 파일 열고 Docker 아이콘을 Applications 폴더로 드래그
3. Applications에서 Docker 실행
4. 권한 허용 후 메뉴바에 고래 아이콘 확인

### 자동 시작 설정
```bash
# Docker Desktop 설정 → "Start Docker Desktop when you log in" 체크
```

### 설치 확인
```bash
docker run hello-world
# "Hello from Docker!" 메시지 확인
```

### 백그라운드 서비스 시작
```bash
# Docker Desktop에서 자동으로 데몬 실행됨
docker ps  # 컨테이너 목록 확인
```