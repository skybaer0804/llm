import os
from datetime import datetime
from pathlib import Path

def update_learning_log(task_name, success_prompt, insights):
    """
    에이전트가 성공한 프롬프트와 인사이트를 CLAUDE.md에 자동 기록하는 스킬
    """
    project_root = Path(__file__).parent
    claude_md_path = project_root / "CLAUDE.md"
    
    log_entry = f"\n### [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {task_name}\n"
    log_entry += f"- **Best Prompt**: `{success_prompt}`\n"
    log_entry += f"- **Insights**: {insights}\n"
    
    # CLAUDE.md 하단에 'Learned Skills' 섹션 업데이트
    try:
        if claude_md_path.exists():
            with open(claude_md_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"✅ CLAUDE.md에 새로운 지식이 기록되었습니다: {task_name}")
        else:
            with open(claude_md_path, "w", encoding="utf-8") as f:
                f.write("# CLAUDE.md - Project Constitution & Learned Skills\n" + log_entry)
            print(f"✅ CLAUDE.md가 생성되고 지식이 기록되었습니다: {task_name}")
    except Exception as e:
        print(f"❌ 지식 베이스 업데이트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    # 테스트용
    # update_learning_log("GPU 최적화", "Metal API 호출 시...", "컨텍스트 윈도우 크기에 따른...")
    pass
