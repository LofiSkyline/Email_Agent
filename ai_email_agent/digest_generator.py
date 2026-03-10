from __future__ import annotations

import os
from datetime import datetime, timezone
from ai_email_agent.models import ProcessedEmail


def generate_digest_markdown(processed_emails: list[ProcessedEmail]) -> str:
    """Groups processed emails by category and generates a Markdown string with indexing."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# 📧 每日邮件情报摘要 ({date_str})", ""]
    
    # 定义分类及其优先级和标题
    # 优先级由列表顺序决定
    category_configs = [
        ("course_info", "🚨 专业课重要通知"),
        ("career_skills", "💡 求职与职业技能"),
        ("cs_activities", "💻 CS 相关活动"),
        ("workshops", "🏫 宣讲会与 Workshop"),
        ("recruitment", "💼 招聘速递 (Brief)"),
        ("other", "📩 其他信息"),
    ]

    # 1. 过滤垃圾邮件并准备索引
    valid_emails = [e for e in processed_emails if e.category != "trash"]
    if not valid_emails:
        return f"# 每日邮件情报摘要 ({date_str})\n\n今天没有需要关注的重要邮件。"

    # 2. 按照分类分组
    by_category: dict[str, list[ProcessedEmail]] = {cfg[0]: [] for cfg in category_configs}
    for email in valid_emails:
        if email.category in by_category:
            by_category[email.category].append(email)

    # 3. 生成内容主体并记录全局索引
    global_index = 1
    index_to_source: dict[int, str] = {}

    for cat_id, title in category_configs:
        emails = by_category[cat_id]
        if not emails:
            continue
            
        lines.append(f"## {title}")
        for email in emails:
            idx_str = f"[{global_index}]"
            index_to_source[global_index] = f"{email.original_subject} (来自: {email.original_sender or '未知'})"
            
            # 根据不同分类调整展示重点
            if cat_id == "recruitment":
                # 招聘信息只做 Brief Introduction
                lines.append(f"- {email.summary} {idx_str}")
            elif cat_id == "workshops":
                # 宣讲会显示具体细节
                lines.append(f"- **摘要**: {email.summary} {idx_str}")
                if email.details:
                    lines.append(f"  - **具体信息**: {email.details}")
            else:
                # 其他常规展示
                lines.append(f"- **重点**: {email.summary} {idx_str}")
                if email.task:
                    lines.append(f"  - **待办**: {email.task}")
                if email.deadline:
                    lines.append(f"  - **截止**: {email.deadline}")
            
            global_index += 1
        lines.append("")

    # 4. 生成文末溯源索引
    lines.append("---")
    lines.append("### 🔍 原始邮件溯源")
    for idx in range(1, global_index):
        lines.append(f"{idx}. {index_to_source[idx]}")

    return "\n".join(lines)


def save_digest(markdown: str, digest_dir: str) -> str:
    """Saves the Markdown digest to a file."""
    if not os.path.exists(digest_dir):
        os.makedirs(digest_dir)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    file_path = os.path.join(digest_dir, f"{date_str}.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
        
    return os.path.abspath(file_path)
