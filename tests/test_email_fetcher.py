from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ai_email_agent.email_fetcher import EmailFetcher


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


class FakeSession:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls: list[tuple[str, dict[str, Any] | None, int]] = []
        self.headers: dict[str, str] = {}

    def get(self, url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> FakeResponse:
        self.calls.append((url, params, timeout))
        return FakeResponse(self.payload)


def test_fetcher_uses_expected_graph_query_params() -> None:
    payload = {
        "value": [
            {
                "id": "1",
                "subject": "Course update",
                "sender": {"emailAddress": {"name": "Admin", "address": "admin@u.edu"}},
                "bodyPreview": "Please note deadline moved",
                "receivedDateTime": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        ]
    }
    fake = FakeSession(payload)

    fetcher = EmailFetcher(access_token="token")
    fetcher.session = fake  # type: ignore[assignment]

    messages = fetcher.fetch_inbox_messages(lookback_hours=24, max_emails=50)

    assert len(messages) == 1
    url, params, _timeout = fake.calls[0]
    assert url.endswith("/me/messages")
    assert params is not None
    assert params["$select"] == "id,subject,sender,bodyPreview,receivedDateTime"
    assert params["$orderby"] == "receivedDateTime desc"
    assert params["$top"] == 50
    assert str(params["$filter"]).startswith("receivedDateTime ge ")
