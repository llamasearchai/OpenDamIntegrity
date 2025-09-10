"""Alerts and notifications: email and SMS (Twilio) with env-based configuration."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from ..config import AlertsConfig

try:
    from twilio.rest import Client  # type: ignore

    TWILIO_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    TWILIO_AVAILABLE = False


def send_email(subject: str, body: str, to_email: str, from_email: str | None = None) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = from_email or os.getenv("SMTP_FROM", user or "noreply@example.com")

    if not host or not user or not password:
        # If SMTP is not configured, do nothing but keep code complete
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def send_sms(body: str, to_number: str) -> None:
    if not TWILIO_AVAILABLE:
        return
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM")
    if not sid or not token or not from_number:
        return
    client = Client(sid, token)
    client.messages.create(body=body, from_=from_number, to=to_number)


def notify(
    level: str,
    message: str,
    config: AlertsConfig,
    email_to: str | None = None,
    sms_to: str | None = None,
) -> None:
    subject = f"OpenDamIntegry Alert: {level}"
    if config.email_enabled and email_to:
        send_email(subject, message, email_to)
    if config.sms_enabled and sms_to:
        send_sms(f"{level}: {message}", sms_to)
