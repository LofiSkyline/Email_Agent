from __future__ import annotations

import logging
import os
from ai_email_agent.config import AppConfig, AgentConfig
from ai_email_agent.digest_generator import generate_digest_markdown, save_digest
from ai_email_agent.email_fetcher import EmailFetcher
from ai_email_agent.email_parser import build_email_text_for_llm
from ai_email_agent.llm_processor import LLMProcessor
from ai_email_agent.models import ProcessedEmail


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def run() -> int:
    config = AppConfig.from_env()
    configure_logging(config.log_level)
    logger = logging.getLogger(__name__)

    # 调试信息：确保路径正确加载
    logger.info("Target directory for reports: %s", config.digest_dir)

    if not config.gmail_user or not config.gmail_app_password:
        logger.error("GMAIL_USER or GMAIL_APP_PASSWORD not set in environment")
        return 1

    logger.info("Connecting to Gmail IMAP as %s", config.gmail_user)
    fetcher = EmailFetcher(user=config.gmail_user, password=config.gmail_app_password)
    
    emails = fetcher.fetch_inbox_messages(
        lookback_hours=config.lookback_hours,
        max_emails=config.max_emails,
    )
    logger.info("Fetched %s emails", len(emails))

    # Pre-warm processors
    processors: dict[str, LLMProcessor] = {
        name: LLMProcessor(agent_cfg) for name, agent_cfg in config.agents.items()
        if agent_cfg.api_key and not agent_cfg.api_key.startswith("sk-") # 过滤掉占位符
    }
    
    default_agent = AgentConfig(
        name="default",
        api_key=config.default_api_key,
        model=config.default_model,
        base_url=config.default_base_url,
        system_prompt=config.default_system_prompt
    )
    default_processor = LLMProcessor(default_agent)

    processed: list[ProcessedEmail] = []
    for email_msg in emails:
        try:
            target_processor = default_processor
            agent_found = "default"
            
            search_content = (
                f"{email_msg.sender} {email_msg.to_recipient} {email_msg.body_preview[:500]}"
            ).lower()

            for agent_name, processor in processors.items():
                if agent_name in search_content:
                    target_processor = processor
                    agent_found = agent_name
                    break
            
            logger.info("Processing email '%s' with agent: %s", email_msg.subject[:30], agent_found)
            
            prompt_text = build_email_text_for_llm(email_msg)
            processed_email = target_processor.process_email_with_llm(prompt_text)
            processed.append(processed_email)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to process email id=%s: %s", email_msg.id, exc)

    if not processed:
        logger.info("No emails processed.")
        return 0

    markdown = generate_digest_markdown(processed)
    output_path = save_digest(markdown, config.digest_dir)

    logger.info("Digest successfully created at: %s", output_path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except Exception as exc:  # noqa: BLE001
        logging.basicConfig(level=logging.ERROR)
        logging.getLogger(__name__).exception("Fatal error: %s", exc)
        raise SystemExit(1) from exc
