# 01. Python 및 가상환경 설정

로컬 LLM 및 AutoGen 개발 환경의 안정성을 위해 Python 가상환경(Virtual Environment)을 구축하는 것은 필수적입니다.

## 1. 가상환경 사용의 이점

- **시스템 Python 보호**: macOS 기본 Python 환경을 건드리지 않아 시스템 오작동을 방지합니다.
- **의존성 충돌 방지**: 프로젝트마다 서로 다른 라이브러리 버전을 독립적으로 관리할 수 있습니다.
- **깔끔한 실험 및 제거**: 특정 프로젝트의 실험이 끝나면 해당 가상환경 폴더만 삭제하여 시스템을 청정하게 유지할 수 있습니다.
- **재현성 확보**: `requirements.txt`를 통해 다른 기기에서도 동일한 개발 환경을 즉시 구축할 수 있습니다.

## 2. 가상환경 구축 가이드 (venv)

Mac M4 Pro 환경에서 추천하는 가장 가볍고 표준적인 방법입니다.

### Step 1: 프로젝트 폴더 생성 및 이동
```bash
mkdir my-autogen-project
cd my-autogen-project
```

### Step 2: 가상환경 생성
```bash
python3 -m venv .venv
```

### Step 3: 가상환경 활성화
```bash
source .venv/bin/activate
```
*활성화되면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다.*

### Step 4: 기본 도구 업데이트
```bash
pip install --upgrade pip setuptools wheel
```

## 3. 가상환경 종료
작업을 마친 후 가상환경을 빠져나오려면 다음 명령어를 입력합니다.
```bash
deactivate
```
