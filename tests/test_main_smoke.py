from __future__ import annotations
from datetime import datetime, timezone

from ai_email_agent import main
from ai_email_agent.models import EmailMessage, ProcessedEmail


class FakeAuth:
    def __init__(self, client_id: str, tenant_id: str) -> None:
        _ = (client_id, tenant_id)

    def get_graph_access_token(self, scopes: list[str] | None = None) -> str:
        _ = scopes
        return "token"


class FakeFetcher:
    def __init__(self, access_token: str) -> None:
        _ = access_token

    def fetch_inbox_messages(self, lookback_hours: int, max_emails: int) -> list[EmailMessage]:
        _ = (lookback_hours, max_emails)
        return [
            EmailMessage(
                id="1",
                subject="Course reminder",
                sender="admin@u.edu",
                body_preview="Submit by tomorrow",
                received_datetime=datetime.now(timezone.utc),
            )
        ]


class FakeLLM:
    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        _ = (api_key, model, base_url)

    def process_email_with_llm(self, email_text: str) -> ProcessedEmail:
        _ = email_text
        return ProcessedEmail(
            category="assignment",
            summary="Assignment due",
            task="Submit coursework",
            deadline="Tomorrow",
        )


def test_main_smoke(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("M365_CLIENT_ID", "client")
    monkeypatch.setenv("M365_TENANT_ID", "tenant")
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.setenv("DIGEST_DIR", str(tmp_path))

    monkeypatch.setattr(main, "GraphAuthenticator", FakeAuth)
    monkeypatch.setattr(main, "EmailFetcher", FakeFetcher)
    monkeypatch.setattr(main, "LLMProcessor", FakeLLM)

    rc = main.run()
    assert rc == 0
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "# Daily Email Digest" in content
    assert "Assignment due" in content
