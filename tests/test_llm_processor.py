from __future__ import annotations

import ai_email_agent.llm_processor as llm_processor
from ai_email_agent.llm_processor import LLMProcessor, _load_json_object, _validate_output


def test_validate_output_invalid_category_falls_back_to_other() -> None:
    result = _validate_output(
        {
            "category": "invalid-category",
            "summary": "Summary",
            "task": "Task",
            "deadline": "Tomorrow",
        }
    )

    assert result.category == "other"
    assert result.summary == "Summary"
    assert result.task == "Task"
    assert result.deadline == "Tomorrow"


def test_load_json_object_malformed_returns_empty_dict() -> None:
    result = _load_json_object("not-json")
    assert result == {}


def test_load_json_object_from_fenced_block() -> None:
    result = _load_json_object(
        """```json
        {"category":"course","summary":"s","task":"t","deadline":"d"}
        ```"""
    )
    assert result["category"] == "course"


def test_validate_output_empty_values_default_cleanly() -> None:
    result = _validate_output({})

    assert result.category == "other"
    assert result.summary == ""
    assert result.task == ""
    assert result.deadline == ""


def test_llm_processor_passes_base_url_to_openai_client(monkeypatch) -> None:
    captured: dict[str, str] = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(llm_processor, "OpenAI", FakeOpenAI)

    _ = LLMProcessor(
        api_key="custom-key",
        model="custom-model",
        base_url="https://example-llm.local/v1",
    )
    assert captured["api_key"] == "custom-key"
    assert captured["base_url"] == "https://example-llm.local/v1"
