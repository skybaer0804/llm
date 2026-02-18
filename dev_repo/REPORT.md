# 📊 Calculator Module Project Report  
**작성일**: 2025-04-05  
**환경**: macOS (M4 Pro), Python 3.12, pytest 9.0.2  
**프로젝트 경로**: `dev_repo/`

---

## 🎯 프로젝트 개요

단순 사칙연산 전용 계산기 모듈을 개발했습니다.  
모듈은 **정수 및 실수 입력**을 지원하며, **덧셈, 뺄셈, 곱셈, 나눗셈**만 처리합니다.  
예외 처리(0으로 나누기, 유효하지 않은 연산자)는 명시적으로 구현되어 안정성을 확보했습니다.

> ✅ **테스트 기반 개발(TDD)** 전략을 적용하여, 기능 구현 전에 전체 테스트 케이스를 먼저 작성하고 검증했습니다.

---

## 🏗️ 아키텍처

### 📁 파일 구조
```
dev_repo/
├── src/
│   └── calculator.py          # 핵심 계산 로직 (4개 함수 + calculate 래퍼)
├── tests/
│   ├── test_calculator.py     # pytest 기반 단위 테스트 (10개 케이스)
│   └── test_example.py        # 기존 예제 테스트 (1개 케이스)
└── .venv/                     # Python 가상환경
```

### 🧠 핵심 설계 원칙
| 항목 | 설명 |
|------|------|
| **단일 책임 원칙** | 각 연산 함수는 하나의 기능만 수행 (`add`, `subtract`, `multiply`, `divide`) |
| **명시적 오류 처리** | `ZeroDivisionError`, `ValueError`는 명시적으로 발생 |
| **확장성 고려** | `calculate(a, b, op)` 래퍼 함수로 향후 연산자 확장 가능 |
| **API 명시** | `__all__`로 공개 인터페이스 명확히 정의 |

---

## 🛠️ 기술 스택

| 구성 요소 | 버전/내용 |
|-----------|-----------|
| **언어** | Python 3.12.12 |
| **테스트 프레임워크** | pytest 9.0.2 |
| **라이브러리** | 표준 라이브러리만 사용 (`math` 불필요) |
| **타입 힌트** | `: float` 일관 적용 (내부 계산 결과는 `float`로 통일) |
| **보안** | `eval`/`exec`/외부 접근/민감 정보 하드코딩 없음 |

---

## ✅ 테스트 통과 지표

### 📊 테스트 결과 요약
| 항목 | 수치 |
|------|------|
| **수행된 테스트 수** | 11개 |
| **통과된 테스트 수** | 11개 |
| **실패/에러 수** | 0개 |
| **실행 시간** | 0.01초 |

### 📋 테스트 케이스 상세
| 테스트 함수 | 입력 | 예상 결과 | 상태 |
|-------------|------|-----------|------|
| `test_add_positive_numbers` | `add(2, 3)` | `5` | ✅ |
| `test_add_negative_numbers` | `add(-1, -4)` | `-5` | ✅ |
| `test_subtract_positive_numbers` | `subtract(10, 7)` | `3` | ✅ |
| `test_subtract_negative_result` | `subtract(3, 5)` | `-2` | ✅ |
| `test_multiply_positive_numbers` | `multiply(4, 5)` | `20` | ✅ |
| `test_multiply_by_zero` | `multiply(7, 0)` | `0` | ✅ |
| `test_divide_positive_numbers` | `divide(10, 2)` | `5.0` | ✅ |
| `test_divide_non_integer_result` | `divide(7, 2)` | `3.5` | ✅ |
| `test_divide_by_zero` | `divide(5, 0)` | `ZeroDivisionError` | ✅ |
| `test_invalid_operator` | `calculate(2, 3, '^')` | `ValueError` | ✅ |
| `test_example` | `example()` | `True` | ✅ |

> 🔍 **특이사항**: `divide()`는 항상 `float` 반환 (`10 / 2 → 5.0`)  
> ⚠️ **예외 처리**: `ZeroDivisionError`는 `pytest.raises()`로 검증

---

## 🔍 리뷰 결과

✅ **READY_TO_COMMIT**

### 검수 항목별 평가
| 항목 | 평가 | 근거 |
|------|------|------|
| **기능 정확성** | ✅ | 설계 시나리오와 100% 일치 |
| **예외 처리** | ✅ | `ZeroDivisionError`, `ValueError` 명시적 발생 |
| **보안성** | ✅ | `eval`/`exec`/외부 접근/민감 정보 없음 |
| **코드 품질** | ✅ | 타입 힌트 일관, `__all__` 명시, pytest 친화적 |
| **확장성** | ✅ | `calculate()` 래퍼로 향후 연산자 확장 가능 |

---

## 📚 Learned Skills

| 항목 | 내용 |
|------|------|
| **테스트 전략** | `pytest.raises()`를 사용한 예외 테스트가 `assert`보다 명확하고 안전함 |
| **타입 힌트** | Python 3.12에서 `float` 반환 타입은 `: float`로 통일하는 것이 일관성 확보에 효과적 |
| **보안 검증** | `grep -r "eval\|exec\|os.system"`을 통한 정적 분석이 빠르고 확실함 |

---

> 📝 **Next Steps (선택적 확장)**  
> - 실수 입력 처리: `str` → `float` 변환 로직 추가 (요구사항 미반영)  
> - 연산자 확장: `calculate()`에 `//`, `%`, `**` 등 추가  
> - CLI 인터페이스: `argparse` 기반 CLI 도구 개발  

---  
**보고서 작성 완료** ✅