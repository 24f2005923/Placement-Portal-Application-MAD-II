"""
gchat_service.py — Google Chat webhook notification helper
───────────────────────────────────────────────────────────
Sends plain-text or card messages to a Google Chat space via an
incoming webhook URL.

Configuration (set in .env):
  GCHAT_WEBHOOK_URL — Full webhook URL from your Google Chat space.
                      Leave blank to disable Google Chat notifications.

To get a webhook URL:
  1. Open Google Chat → your space → Manage webhooks
  2. Click "Add webhook", give it a name
  3. Copy the generated URL into your .env file
"""

import json
import logging
import urllib.request
import urllib.error
from flask import current_app

logger = logging.getLogger(__name__)


def send_gchat_message(text: str) -> bool:
    """
    Send a simple text message to the configured Google Chat space.

    Args:
        text: Plain text message to send.

    Returns:
        True on success or if webhooks are not configured,
        False if the HTTP request failed.
    """
    webhook_url = current_app.config.get('GCHAT_WEBHOOK_URL', '').strip()

    # ── Webhook not configured — skip silently ────────────────────
    if not webhook_url:
        logger.debug('Google Chat webhook not configured — skipping message.')
        return True   # not a failure, just not enabled

    payload = json.dumps({'text': text}).encode('utf-8')

    try:
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                logger.info('Google Chat message sent successfully.')
                return True
            else:
                logger.warning(
                    'Google Chat webhook returned status %d', response.status
                )
                return False

    except urllib.error.URLError as url_err:
        logger.error('Google Chat webhook request failed: %s', url_err)
        return False
    except Exception as exc:
        logger.error('Unexpected error sending Google Chat message: %s', exc)
        return False


def send_gchat_card(title: str, subtitle: str, body_text: str) -> bool:
    """
    Send a structured card message to Google Chat.

    Cards look nicer than plain text — they have a title bar and
    formatted body.  Falls back to plain text if the webhook is not
    configured.

    Args:
        title:     Bold header of the card.
        subtitle:  Secondary text below the title.
        body_text: Main message body.

    Returns:
        True on success, False on failure.
    """
    webhook_url = current_app.config.get('GCHAT_WEBHOOK_URL', '').strip()

    if not webhook_url:
        logger.debug('Google Chat webhook not configured — skipping card.')
        return True

    # Google Chat card v1 format
    card_payload = {
        'cards': [{
            'header': {
                'title': title,
                'subtitle': subtitle,
            },
            'sections': [{
                'widgets': [{
                    'textParagraph': {'text': body_text}
                }]
            }]
        }]
    }

    payload = json.dumps(card_payload).encode('utf-8')

    try:
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                logger.info('Google Chat card sent successfully.')
                return True
            else:
                logger.warning(
                    'Google Chat card webhook returned status %d', response.status
                )
                return False

    except Exception as exc:
        logger.error('Error sending Google Chat card: %s', exc)
        return False


def send_gchat_notification(title: str, text: str = None) -> bool:
    """Helper alias to send notification card or text message to Google Chat."""
    if text is None:
        return send_gchat_message(title)
    return send_gchat_card(title, "Placement Portal Notification", text)
