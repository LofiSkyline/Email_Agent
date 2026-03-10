from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

# 根据你的需求定制的分类
EmailCategory = Literal[
    "course_info",      # 专业课通知 (最高优先级)
    "career_skills",    # 求职职业技能 (普通重要)
    "cs_activities",    # CS 相关活动 (重要)
    "workshops",        # 宣讲会/研讨会 (提取时间地点)
    "recruitment",      # 招聘信息 (简单摘要)
    "trash",            # 广告/BUCS/不重要 (将被过滤)
    "other",
]

VALID_CATEGORIES: set[str] = {
    "course_info",
    "career_skills",
    "cs_activities",
    "workshops",
    "recruitment",
    "trash",
    "other",
}


@dataclass(slots=True)
class EmailMessage:
    id: str
    subject: str
    sender: str
    body_preview: str
    received_datetime: datetime
    to_recipient: str = ""


@dataclass(slots=True)
class ProcessedEmail:
    category: EmailCategory
    summary: str
    task: str
    deadline: str
    original_sender: str = ""
    original_subject: str = "" # 新增：保存原始标题用于文末索引
    details: str = ""          # 新增：保存时间地点等具体信息
