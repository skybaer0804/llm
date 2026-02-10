# AutoGen 시스템 운영 가이드

## 📊 시스템 완성도 체크리스트

✅ Ollama 실행 중
✅ 3개 Qwen3 모델 로드됨
✅ Router.py 실행 중 (포트 8000)
✅ AutoGen 에이전트 팀 준비됨
✅ GitHub 모니터 24시간 실행 중

→ 완전한 자동화 개발 시스템 완성!

## ❓ 자주 나오는 질문 (FAQ)

**Q: 라우터가 응답 안 함?**
A: `curl http://localhost:8000/health` 확인 → Ollama 재시작

**Q: AutoGen이 토큰 초과?**
A: `max_tokens` 줄이기 또는 `max_round` 감소

**Q: GitHub 모니터가 실행 안 됨?**
A: `launchctl list` → `gh auth status` 확인
