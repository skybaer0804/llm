# AutoGen 기초 환경 확인

## 📋 현재 상태 체크

먼저 모든 게 정상인지 확인해봅시다.

```bash
# 1. Ollama 실행 확인
curl http://localhost:11434

# 2. 모델들 확인
ollama list
# 예상 출력:
# qwen3-coder-next:q4_K_M
# qwen3-coder:32b
# qwen3:14b

# 3. 각 모델 간단히 테스트
ollama run qwen3-coder-next:q4_K_M "안녕!"
# Ctrl+D로 종료

ollama run qwen3-coder:32b "파이썬 함수 만들어줄래"
# Ctrl+D로 종료

ollama run qwen3:14b "이 코드 검수해줄래"
# Ctrl+D로 종료
```

모두 응답이 나오면 ✅ 완료입니다.