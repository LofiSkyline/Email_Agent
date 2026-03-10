from __future__ import annotations

from ai_email_agent.models import EmailMessage


def build_email_text_for_llm(email: EmailMessage, max_body_chars: int = 1200) -> str:
    subject = (email.subject or "(No Subject)").strip()
    sender = (email.sender or "Unknown sender").strip()
    body_preview = (email.body_preview or "").strip().replace("\n", " ")

    if len(body_preview) > max_body_chars:
        body_preview = body_preview[:max_body_chars].rstrip() + "..."

    received = email.received_datetime.isoformat()

    return (
        f"Subject: {subject}\n"
        f"Sender: {sender}\n"
        f"Received: {received}\n"
        f"Body Preview: {body_preview}"
    )
