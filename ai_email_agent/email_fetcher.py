from __future__ import annotations

import email
import imaplib
import logging
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from typing import Any

from ai_email_agent.models import EmailMessage

logger = logging.getLogger(__name__)


class EmailFetcher:
    IMAP_SERVER = "imap.gmail.com"

    def __init__(self, user: str, password: str) -> None:
        self.user = user
        self.password = password

    def fetch_inbox_messages(self, lookback_hours: int = 24, max_emails: int = 50) -> list[EmailMessage]:
        if not self.user or not self.password:
            raise ValueError("GMAIL_USER and GMAIL_APP_PASSWORD must be set")

        try:
            mail = imaplib.IMAP4_SSL(self.IMAP_SERVER)
            mail.login(self.user, self.password)
            mail.select("inbox")

            # Calculate date for IMAP search (e.g. 10-Mar-2024)
            since_date = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE "{since_date}")')

            if status != "OK":
                logger.error("Failed to search emails")
                return []

            email_ids = messages[0].split()
            # Get latest emails first
            email_ids = email_ids[::-1][:max_emails]

            fetched_messages: list[EmailMessage] = []
            for e_id in email_ids:
                status, msg_data = mail.fetch(e_id, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        fetched_messages.append(self._parse_email(e_id.decode(), msg))

            mail.logout()
            return fetched_messages

        except Exception as e:
            logger.exception("Error fetching emails via IMAP: %s", e)
            return []

    def _parse_email(self, msg_id: str, msg: email.message.Message) -> EmailMessage:
        subject = self._decode_header_str(msg.get("Subject", "(No Subject)"))
        sender = self._decode_header_str(msg.get("From", "Unknown Sender"))
        to_recipient = self._decode_header_str(msg.get("To", ""))

        # Extraction of date
        date_str = msg.get("Date")
        try:
            received_datetime = email.utils.parsedate_to_datetime(date_str)
        except Exception:
            received_datetime = datetime.now(timezone.utc)

        # Extraction of body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="ignore")

        # In our case, we might want to store 'to_recipient' in the model to use it for prompt routing later
        # For now, let's keep the model simple but we'll adapt it if needed
        return EmailMessage(
            id=msg_id,
            subject=subject,
            sender=sender,
            body_preview=body[:2000],  # Increased preview size for better LLM context
            received_datetime=received_datetime,
            to_recipient=to_recipient, # We'll need to update the model to include this
        )

    def _decode_header_str(self, header_value: str) -> str:
        decoded_list = decode_header(header_value)
        result = ""
        for content, charset in decoded_list:
            if isinstance(content, bytes):
                result += content.decode(charset or "utf-8", errors="ignore")
            else:
                result += str(content)
        return result
