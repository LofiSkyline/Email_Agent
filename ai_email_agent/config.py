from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass(slots=True)
class AgentConfig:
    name: str
    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str | None = None
    system_prompt: str | None = None


@dataclass(slots=True)
class AppConfig:
    # Gmail Credentials
    gmail_user: str
    gmail_app_password: str

    # Default LLM Settings
    default_api_key: str
    default_model: str = "gpt-4o-mini"
    default_base_url: str | None = None
    default_system_prompt: str | None = None

    # Processing Settings
    lookback_hours: int = 24
    max_emails: int = 50
    digest_dir: str = "daily_digest"
    log_level: str = "INFO"

    # Dynamic Agent Configurations
    agents: dict[str, AgentConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> AppConfig:
        # 强制加载 .env 并覆盖现有环境变量
        load_dotenv(override=True)

        # 处理路径：展开 ~ 并转为绝对路径
        raw_digest_dir = os.environ.get("DIGEST_DIR", "daily_digest")
        abs_digest_dir = os.path.abspath(os.path.expanduser(raw_digest_dir))

        config = cls(
            gmail_user=os.environ.get("GMAIL_USER", ""),
            gmail_app_password=os.environ.get("GMAIL_APP_PASSWORD", ""),
            default_api_key=os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY", ""),
            default_model=os.environ.get("LLM_MODEL") or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            default_base_url=os.environ.get("LLM_BASE_URL"),
            default_system_prompt=os.environ.get("DEFAULT_SYSTEM_PROMPT"),
            lookback_hours=int(os.environ.get("LOOKBACK_HOURS", "24")),
            max_emails=int(os.environ.get("MAX_EMAILS", "50")),
            digest_dir=abs_digest_dir,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )

        agent_patterns = re.compile(r"^EMAIL_AGENT_([A-Z0-9]+)_(API_KEY|BASE_URL|MODEL|SYSTEM_PROMPT)$")
        for key, value in os.environ.items():
            match = agent_patterns.match(key)
            if match:
                agent_name = match.group(1).lower()
                attr_type = match.group(2).lower()
                if agent_name not in config.agents:
                    config.agents[agent_name] = AgentConfig(name=agent_name, api_key=config.default_api_key)
                
                if attr_type == "api_key":
                    config.agents[agent_name].api_key = value
                elif attr_type == "base_url":
                    config.agents[agent_name].base_url = value
                elif attr_type == "model":
                    config.agents[agent_name].model = value
                elif attr_type == "system_prompt":
                    config.agents[agent_name].system_prompt = value
        
        return config
