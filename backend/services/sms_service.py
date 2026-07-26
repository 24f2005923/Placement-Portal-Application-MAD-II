"""
sms_service.py — Pluggable SMS provider abstraction
─────────────────────────────────────────────────────
Defines an abstract SMS provider interface so the rest of the
application can send SMS messages without knowing which provider
is being used.

Available providers:
  • ConsoleSMSProvider  (default) — prints messages to logs.
                                     No API key or account needed.
                                     Perfect for development.
  • TwilioSMSProvider             — sends real SMS via Twilio REST API.
                                     Requires TWILIO_* env vars.

Configuration (set in .env):
  SMS_PROVIDER=console   (or "twilio")
  TWILIO_ACCOUNT_SID=...
  TWILIO_AUTH_TOKEN=...
  TWILIO_FROM_NUMBER=+1XXXXXXXXXX

Usage in tasks:
  from services.sms_service import get_sms_provider
  sms = get_sms_provider()
  sms.send(to='+919876543210', message='Your interview is tomorrow!')
"""

import logging
from abc import ABC, abstractmethod
from flask import current_app

logger = logging.getLogger(__name__)


# ── Abstract base ─────────────────────────────────────────────────

class SMSProvider(ABC):
    """
    Abstract base class for SMS providers.

    Any new SMS provider (e.g. MSG91, Vonage) only needs to
    implement the `send` method below.
    """

    @abstractmethod
    def send(self, to: str, message: str) -> bool:
        """
        Send an SMS message.

        Args:
            to:      Recipient phone number in E.164 format (+91XXXXXXXXXX).
            message: SMS body text (keep under 160 characters for a single SMS).

        Returns:
            True on success, False on failure.
        """
        raise NotImplementedError


# ── Console provider (development default) ────────────────────────

class ConsoleSMSProvider(SMSProvider):
    """
    Development SMS provider that logs messages to the console.

    No external service or API key is needed.  Use this during
    development and switch to a real provider in production.
    """

    def send(self, to: str, message: str) -> bool:
        logger.info(
            '[SMS — CONSOLE MODE]\n'
            '  To: %s\n'
            '  Message: %s',
            to, message
        )
        return True


# ── Twilio provider ───────────────────────────────────────────────

class TwilioSMSProvider(SMSProvider):
    """
    Production SMS provider using the Twilio REST API.

    Requires the twilio package (already bundled with celery extras).
    Set SMS_PROVIDER=twilio and the TWILIO_* environment variables
    in your .env file to activate this provider.
    """

    def send(self, to: str, message: str) -> bool:
        account_sid  = current_app.config.get('TWILIO_ACCOUNT_SID', '')
        auth_token   = current_app.config.get('TWILIO_AUTH_TOKEN', '')
        from_number  = current_app.config.get('TWILIO_FROM_NUMBER', '')

        if not all([account_sid, auth_token, from_number]):
            logger.error(
                'Twilio is selected as SMS provider but TWILIO_ACCOUNT_SID, '
                'TWILIO_AUTH_TOKEN, or TWILIO_FROM_NUMBER is not set.'
            )
            return False

        try:
            # Import Twilio only when actually needed so the application
            # doesn't fail on startup if twilio is not installed.
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            msg = client.messages.create(
                body=message,
                from_=from_number,
                to=to,
            )
            logger.info('SMS sent via Twilio to %s | SID: %s', to, msg.sid)
            return True

        except ImportError:
            logger.error(
                'Twilio package is not installed.  Run: pip install twilio'
            )
            return False
        except Exception as exc:
            logger.error('Twilio SMS failed to %s: %s', to, exc)
            return False


# ── Factory function ──────────────────────────────────────────────

def get_sms_provider() -> SMSProvider:
    """
    Return the configured SMS provider instance.

    Reads SMS_PROVIDER from Flask config.  Defaults to the console
    provider if the value is not recognised.

    Returns:
        An instance of SMSProvider (ConsoleSMSProvider or TwilioSMSProvider).
    """
    provider_name = current_app.config.get('SMS_PROVIDER', 'console').lower()

    providers = {
        'console': ConsoleSMSProvider,
        'twilio':  TwilioSMSProvider,
    }

    provider_class = providers.get(provider_name, ConsoleSMSProvider)
    logger.debug('Using SMS provider: %s', provider_class.__name__)
    return provider_class()
