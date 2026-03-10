from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from ai_email_agent.config import AgentConfig
from ai_email_agent.models import ProcessedEmail, VALID_CATEGORIES


class LLMProcessor:
    def __init__(self, agent_config: AgentConfig) -> None:
        client_kwargs: dict[str, Any] = {"api_key": agent_config.api_key}
        if agent_config.base_url:
            client_kwargs["base_url"] = agent_config.base_url
        self.client = OpenAI(**client_kwargs)
        self.model = agent_config.model
        self.system_prompt = agent_config.system_prompt or "You are an efficient personal assistant."

    def process_email_with_llm(self, email_text: str) -> ProcessedEmail:
        prompt = (
            f"{self.system_prompt}\n\n"
            "Return strictly valid JSON with keys: category, summary, task, deadline, original_sender, original_subject, details.\n"
            "Allowed categories: course_info, career_skills, cs_activities, workshops, recruitment, trash, other.\n"
            "Do not include markdown or extra text.\n\n"
            f"Email Content:\n{email_text}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        raw_text = (response.choices[0].message.content or "").strip()
        data = _load_json_object(raw_text)
        return _validate_output(data)


def _load_json_object(text: str) -> dict[str, Any]:
    if not text:
        return {}

    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        try:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if match:
                loaded = json.loads(match.group(0))
            else:
                return {}
        except Exception:
            return {}

    if isinstance(loaded, dict):
        return loaded
    return {}


def _validate_output(data: dict[str, Any]) -> ProcessedEmail:
    category = str(data.get("category", "other")).strip().lower()
    if category not in VALID_CATEGORIES:
        category = "other"

    return ProcessedEmail(
        category=category,  # type: ignore[arg-type]
        summary=str(data.get("summary", "")).strip(),
        task=str(data.get("task", "")).strip(),
        deadline=str(data.get("deadline", "")).strip(),
        original_sender=str(data.get("original_sender", "")).strip(),
        original_subject=str(data.get("original_subject", "")).strip(),
        details=str(data.get("details", "")).strip(),
    )
