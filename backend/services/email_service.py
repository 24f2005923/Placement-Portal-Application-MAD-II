"""
email_service.py — Email notification helper
─────────────────────────────────────────────
Sends HTML emails via SMTP using Python's built-in smtplib.

Configuration (set in .env):
  MAIL_SERVER   — SMTP server hostname  (default: smtp.gmail.com)
  MAIL_PORT     — SMTP port             (default: 587)
  MAIL_USE_TLS  — Enable STARTTLS       (default: true)
  MAIL_USERNAME — Sender account email  (leave blank for console mode)
  MAIL_PASSWORD — Sender account password / app-password
  MAIL_SENDER   — From address shown to recipients

Console mode:
  If MAIL_USERNAME is not configured the email body is printed to
  the console/logs instead of being sent.  This is useful during
  development so no SMTP server is needed.
"""

import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from flask import current_app

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body_html: str, attachments: list = None) -> bool:
    """
    Send an HTML email to one recipient.

    Args:
        to:        Recipient email address.
        subject:   Email subject line.
        body_html: HTML content for the email body.
        attachments: Optional list of file paths to attach.

    Returns:
        True if the email was sent (or logged in console mode),
        False if an error occurred.
    """
    server   = current_app.config.get('MAIL_SERVER', '')

    # ── Console mode — explicitly set to console or empty ─────────
    if not server or server.lower() == 'console':
        logger.info(
            '[EMAIL — CONSOLE MODE]\n'
            '  To: %s\n'
            '  Subject: %s\n'
            '  Body (HTML stripped):\n%s',
            to, subject, _strip_html(body_html)
        )
        return True   # treat as success so tasks don't retry unnecessarily

    # ── Real SMTP send ────────────────────────────────────────────
    try:
        port     = current_app.config['MAIL_PORT']
        use_tls  = current_app.config['MAIL_USE_TLS']
        username = current_app.config.get('MAIL_USERNAME', '')
        password = current_app.config.get('MAIL_PASSWORD', '')
        sender   = current_app.config['MAIL_SENDER']

        # Build the MIME message.
        message = MIMEMultipart('mixed')
        message['Subject'] = subject
        message['From']    = sender
        message['To']      = to

        alternative = MIMEMultipart('alternative')
        alternative.attach(MIMEText(body_html, 'html'))
        message.attach(alternative)

        for attachment_path in attachments or []:
            if not attachment_path or not os.path.isfile(attachment_path):
                logger.warning('Skipping missing email attachment: %s', attachment_path)
                continue

            with open(attachment_path, 'rb') as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                'attachment',
                filename=os.path.basename(attachment_path),
            )
            message.attach(part)

        # Connect and send.
        with smtplib.SMTP(server, port) as smtp_conn:
            if use_tls:
                smtp_conn.starttls()
            if username:
                smtp_conn.login(username, password)
            smtp_conn.sendmail(sender, [to], message.as_string())

        logger.info('Email sent to %s | Subject: %s', to, subject)
        return True

    except smtplib.SMTPException as smtp_err:
        logger.error('SMTP error sending email to %s: %s', to, smtp_err)
        return False
    except Exception as exc:
        logger.error('Unexpected error sending email to %s: %s', to, exc)
        return False


def send_bulk_emails(recipients: list, subject: str, body_html: str) -> dict:
    """
    Send the same email to multiple recipients.

    Args:
        recipients: List of email address strings.
        subject:    Email subject.
        body_html:  HTML email body.

    Returns:
        Dict with 'sent' (int) and 'failed' (int) counts.
    """
    sent_count   = 0
    failed_count = 0

    for recipient in recipients:
        if send_email(recipient, subject, body_html):
            sent_count += 1
        else:
            failed_count += 1

    logger.info('Bulk email done: %d sent, %d failed', sent_count, failed_count)
    return {'sent': sent_count, 'failed': failed_count}


# ── Internal helpers ──────────────────────────────────────────────

def _strip_html(html: str) -> str:
    """Very simple HTML tag remover for readable console output."""
    import re
    return re.sub(r'<[^>]+>', '', html).strip()
