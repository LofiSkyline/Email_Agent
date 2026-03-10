from __future__ import annotations

import os

import pytest

from ai_email_agent.config import AppConfig


@pytest.fixture(autouse=True)
def clear_env() -> None:
    keys = [
        "M365_CLIENT_ID",
        "M365_TENANT_ID",
        "LLM_API_KEY",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "LOOKBACK_HOURS",
        "MAX_EMAILS",
        "DIGEST_DIR",
        "LOG_LEVEL",
    ]
    old = {k: os.environ.get(k) for k in keys}
    for key in keys:
        os.environ.pop(key, None)
    yield
    for key, value in old.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def test_config_requires_env_vars() -> None:
    with pytest.raises(ValueError) as exc:
        AppConfig.from_env()

    assert "M365_CLIENT_ID" in str(exc.value)
    assert "M365_TENANT_ID" in str(exc.value)
    assert "LLM_API_KEY (or OPENAI_API_KEY)" in str(exc.value)


def test_config_defaults() -> None:
    os.environ["M365_CLIENT_ID"] = "client"
    os.environ["M365_TENANT_ID"] = "tenant"
    os.environ["OPENAI_API_KEY"] = "key"

    cfg = AppConfig.from_env()

    assert cfg.llm_api_key == "key"
    assert cfg.llm_model == "gpt-5-mini"
    assert cfg.llm_base_url is None
    assert cfg.lookback_hours == 24
    assert cfg.max_emails == 50
    assert str(cfg.digest_dir) == "daily_digest"
    assert cfg.log_level == "INFO"


def test_config_prefers_llm_specific_env_vars() -> None:
    os.environ["M365_CLIENT_ID"] = "client"
    os.environ["M365_TENANT_ID"] = "tenant"
    os.environ["OPENAI_API_KEY"] = "openai_key"
    os.environ["OPENAI_MODEL"] = "openai_model"
    os.environ["LLM_API_KEY"] = "custom_key"
    os.environ["LLM_MODEL"] = "custom_model"
    os.environ["LLM_BASE_URL"] = "https://example-llm.local/v1"

    cfg = AppConfig.from_env()

    assert cfg.llm_api_key == "custom_key"
    assert cfg.llm_model == "custom_model"
    assert cfg.llm_base_url == "https://example-llm.local/v1"
