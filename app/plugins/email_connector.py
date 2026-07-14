"""
APEX - AI Accounts Payable & Receivable Engine
"""
import aiosmtplib
import logging
from email.message import EmailMessage
from app.config import settings

class EmailConnector:
    """Conector SMTP para envio assíncrono de campanhas de Dunning."""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.EMAIL_FROM
        self.dry_run = settings.EMAIL_DRY_RUN

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Envia e-mail ou apenas simula (dry_run)."""
        if self.dry_run:
            logging.info(f"DRY RUN: Would send email to {to_email} | Subject: '{subject}'")
            return True

        if not self.host or not self.user or not self.password:
            logging.error("Email credentials not configured.")
            return False

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                use_tls=self.use_tls
            )
            return True
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
            return False
