from __future__ import annotations

from ai_email_agent.digest_generator import generate_digest_markdown, save_digest
from ai_email_agent.models import ProcessedEmail


def test_digest_sections_grouped_correctly(tmp_path) -> None:
    items = [
        ProcessedEmail(category="assignment", summary="Networking coursework due", task="Submit report", deadline="2026-03-15"),
        ProcessedEmail(category="event", summary="CSS Ball reminder", task="", deadline=""),
        ProcessedEmail(category="other", summary="Promotional email", task="", deadline=""),
    ]

    markdown = generate_digest_markdown(items)

    assert "## Important" in markdown
    assert "Networking coursework due" in markdown
    assert "## Tasks" in markdown
    assert "Submit report" in markdown
    assert "## Events" in markdown
    assert "CSS Ball reminder" in markdown
    assert "## Other" in markdown
    assert "Promotional email" in markdown

    out = save_digest(markdown, tmp_path)
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("# Daily Email Digest")
