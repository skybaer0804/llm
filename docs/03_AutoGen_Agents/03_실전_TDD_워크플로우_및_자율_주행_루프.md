# 03. 실전 TDD 워크플로우 및 자율 주행 루프

에이전시가 단순히 코드를 생성하는 것을 넘어, 실제 로컬 Git 저장소와 상주형 샌드박스를 활용하여 스스로 테스트하고 구현을 완성해 나가는 실전적인 워크플로우를 설계합니다.

## 1. 실전 샌드박스 전략: "컨테이너는 하나만, 통로는 공유"

TDD 루프마다 컨테이너를 껐다 켜는 대신, 에이전시 시작 시 컨테이너를 하나 띄우고 호스트의 프로젝트 폴더를 마운트(Mount)하여 사용합니다.

- **구조**: 호스트의 `./my-project` 폴더 ↔ 컨테이너의 `/app` 폴더 실시간 동기화.
- **보안**: 컨테이너 내부에 필요한 도구(pytest, pylint 등)만 설치하고 인터넷은 차단합니다.
- **속도**: `exec_run`을 활용해 이미 실행 중인 컨테이너에 명령만 전달하여 지연 시간을 최소화합니다.

## 2. 전체 워크플로우 시나리오 (Git 기반)

사용자가 "로그인 기능 만들어줘"라고 요청했을 때의 실제 구동 흐름입니다.

### Step 1: Architect의 설계
- **모델**: Qwen2.5-72B (52GB 로드)
- **동작**: 전체 구조 설계 및 `tests/test_login.py` 시나리오 확정.
- **결과**: JSON 형태의 상세 설계 가이드 생성 및 모델 언로드.

### Step 2: Reviewer의 테스트 코드 작성
- **모델**: Qwen2.5-14B (VRAM 상주)
- **동작**: 설계 가이드를 바탕으로 실제 로컬 디렉토리에 테스트 파일 작성.
- **파일 생성**: `./my-project/tests/test_login.py`

### Step 3: Local Executor의 실행 (Docker)
- **동작**: 이미 떠 있는 상주형 컨테이너에게 명령 전달.
- **명령**: `container.exec_run("pytest tests/test_login.py")`
- **결과**: 실패 로그(Red) 확인.

### Step 4: Coder의 구현
- **모델**: Qwen2.5-32B (VRAM 상주)
- **동작**: 실패 로그를 분석하여 실제 비즈니스 로직 구현.
- **파일 수정**: `./my-project/app/auth.py`

### Step 5: 반복 (Green & Refactor)
- 테스트가 통과(Green)할 때까지 Step 3과 Step 4를 반복합니다.

## 3. TDD 자율 주행 루프 (Main Engine) 설계

모든 부품을 조립하여 [요구사항 → 설계 → 테스트 → 구현 → 커밋]까지 이어지는 파이썬 메인 엔진 예시입니다.

```python
def tdd_autonomous_loop(user_requirement):
    # 1. Architect 설계 (거대 모델 호출)
    plan = call_architect(user_requirement)
    
    # 2. Reviewer 테스트 코드 작성 (상주 모델)
    test_code = call_reviewer_for_test(plan)
    tools.write_file("tests/test_feature.py", test_code)
    
    # 3. TDD 사이클 시작
    max_retries = 5
    for i in range(max_retries):
        # 테스트 실행 (Docker exec_run 활용)
        test_result = tools.run_test()
        
        if test_result['exit_code'] == 0:
            print("🎉 테스트 통과!")
            # 성공 시 자동 Git 커밋
            tools.git_commit(f"feat: {user_requirement} 구현 완료")
            break
        else:
            print(f"🔄 테스트 실패 (시도 {i+1}/{max_retries}). 수정 중...")
            # Coder가 실패 로그를 보고 코드 수정 (상주 모델)
            new_code = call_coder_fix(test_result['output'])
            tools.write_file("app/feature.py", new_code)
            
    # 4. 최종 리포트 생성
    generate_final_report(plan, "app/feature.py", test_result['output'])
```

## 4. 이 방식의 장점

1.  **Git 연동**: LLM이 작성한 코드가 즉시 로컬 폴더에 반영되므로, 사용자가 바로 `git commit` 상태를 확인하거나 추가 작업을 이어갈 수 있습니다.
2.  **M4 Pro 최적화**: `exec_run`은 프로세스 접근 방식이므로 지연 시간이 거의 없습니다.
3.  **환경 일관성**: 컨테이너 내부에 필요한 라이브러리를 한 번만 설치해두면, 모든 에이전트가 동일한 환경에서 검증을 수행합니다.
