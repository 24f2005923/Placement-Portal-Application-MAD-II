"""
interview_reminders.py — Daily interview reminder Celery task
──────────────────────────────────────────────────────────────
This module defines a scheduled Celery task that runs every day
at 08:00 UTC.  It finds all students who have an interview
scheduled within the next 24–48 hours and sends them:

  1. An email reminder
  2. A Google Chat notification (if GCHAT_WEBHOOK_URL is configured)
  3. An SMS reminder (via the configured SMS provider)

The Beat schedule is defined in celery_app.py.

Retry policy:
  • Retries up to 3 times with a 5-minute delay between attempts.
  • If all retries fail the task is marked FAILURE in the result backend.
"""

import logging
from datetime import date, timedelta

from celery_app import celery
from models import db
from models.interview import Interview
from models.application import Application
from models.student import Student
from services.email_service import send_email
from services.gchat_service import send_gchat_message
from services.sms_service import get_sms_provider

logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.interview_reminders.send_interview_reminders',
    bind=True,
    max_retries=3,
    default_retry_delay=300,   # retry after 5 minutes
)
def send_interview_reminders(self):
    """
    Scheduled task: send interview reminders to students.

    Finds all interviews scheduled for today + tomorrow, then
    dispatches Email, Google Chat, and SMS notifications for each.

    This task is automatically triggered daily by Celery Beat.
    You can also trigger it manually from the Celery CLI:
      celery -A celery_app call tasks.interview_reminders.send_interview_reminders
    """
    logger.info('=== Interview Reminder Task Started ===')

    try:
        today    = date.today()
        tomorrow = today + timedelta(days=1)

        # Find all interviews scheduled for today or tomorrow
        # that are still in the 'interview' stage (not yet concluded).
        upcoming_interviews = (
            db.session.query(Interview)
            .join(Application, Interview.application_id == Application.id)
            .filter(
                Interview.interview_date.in_([today, tomorrow]),
                Application.application_status == 'interview',
            )
            .all()
        )

        if not upcoming_interviews:
            logger.info('No upcoming interviews found for %s / %s. Task done.', today, tomorrow)
            return {
                'status': 'completed',
                'reminders_sent': 0,
                'date_checked': str(today),
            }

        reminders_sent = 0
        sms_provider = get_sms_provider()

        for interview in upcoming_interviews:
            # Load the associated student through the application relationship.
            application = interview.application
            if application is None:
                continue

            student = application.student
            if student is None:
                continue

            user = student.user
            if user is None:
                continue

            # Build human-readable interview details.
            interview_info = _build_interview_info(interview, application)

            # ── 1. Email reminder ─────────────────────────────────
            email_subject = f"Interview Reminder: {interview_info['company']} — {interview_info['interview_date']}"
            email_body    = _build_email_body(user.name, interview_info)
            send_email(to=user.email, subject=email_subject, body_html=email_body)

            # ── 2. Google Chat notification ───────────────────────
            gchat_text = (
                f"🗓️ *Interview Reminder* — {user.name}\n"
                f"Company: {interview_info['company']}\n"
                f"Role: {interview_info['role']}\n"
                f"Date: {interview_info['interview_date']} at {interview_info['interview_time']}\n"
                f"Mode: {interview_info['mode']}"
            )
            send_gchat_message(gchat_text)

            # ── 3. SMS reminder ───────────────────────────────────
            if student.phone:
                sms_body = (
                    f"Hi {user.name}, your interview with {interview_info['company']} "
                    f"is on {interview_info['interview_date']} at {interview_info['interview_time']}. "
                    f"Mode: {interview_info['mode']}. All the best!"
                )
                sms_provider.send(to=student.phone, message=sms_body)

            reminders_sent += 1
            logger.info(
                'Reminder sent to %s (%s) for interview on %s',
                user.name, user.email, interview_info['interview_date']
            )

        logger.info('=== Interview Reminder Task Done: %d reminders sent ===', reminders_sent)
        return {
            'status': 'completed',
            'reminders_sent': reminders_sent,
            'date_checked': str(today),
        }

    except Exception as exc:
        logger.error('Interview reminder task failed: %s', exc, exc_info=True)
        # Retry automatically up to max_retries times.
        raise self.retry(exc=exc)


# ── Private helpers ───────────────────────────────────────────────

def _build_interview_info(interview, application) -> dict:
    """
    Extract readable interview details into a plain dictionary.

    This keeps the task function clean and the template building
    code separate.
    """
    drive   = application.drive
    company = drive.company if drive else None

    return {
        'company':        company.company_name if company else 'Unknown Company',
        'role':           drive.job_role if drive else 'Unknown Role',
        'interview_date': interview.interview_date.strftime('%d %B %Y') if interview.interview_date else 'TBD',
        'interview_time': interview.interview_time or 'Time not specified',
        'mode':           interview.interview_mode or 'online',
        'link':           interview.interview_link or '',
        'round_name':     interview.round_name or 'Interview',
        'remarks':        interview.remarks or '',
    }


def _build_email_body(student_name: str, info: dict) -> str:
    """
    Build an HTML email body for the interview reminder.

    Returns a styled HTML string.
    """
    link_section = ''
    if info['mode'] == 'online' and info['link']:
        link_section = f'<p><strong>Meeting Link:</strong> <a href="{info["link"]}">{info["link"]}</a></p>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body        {{ font-family: Arial, sans-serif; color: #333; background: #f5f5f5; margin: 0; padding: 0; }}
        .container  {{ max-width: 600px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header     {{ background: #4f46e5; color: #fff; padding: 28px 32px; }}
        .header h1  {{ margin: 0; font-size: 22px; }}
        .body       {{ padding: 28px 32px; }}
        .body p     {{ line-height: 1.6; }}
        .info-box   {{ background: #f0f0ff; border-left: 4px solid #4f46e5; padding: 16px 20px; border-radius: 4px; margin: 20px 0; }}
        .info-box p {{ margin: 6px 0; }}
        .footer     {{ background: #f9f9f9; padding: 16px 32px; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🗓️ Interview Reminder</h1>
        </div>
        <div class="body">
          <p>Dear <strong>{student_name}</strong>,</p>
          <p>This is a friendly reminder that you have an upcoming interview scheduled.</p>
          <div class="info-box">
            <p><strong>Company:</strong> {info['company']}</p>
            <p><strong>Role:</strong> {info['role']}</p>
            <p><strong>Round:</strong> {info['round_name']}</p>
            <p><strong>Date:</strong> {info['interview_date']}</p>
            <p><strong>Time:</strong> {info['interview_time']}</p>
            <p><strong>Mode:</strong> {info['mode'].title()}</p>
            {link_section}
            {'<p><strong>Remarks:</strong> ' + info['remarks'] + '</p>' if info['remarks'] else ''}
          </div>
          <p>Please be on time and make sure your internet connection is stable (for online interviews).</p>
          <p><strong>Best of luck!</strong></p>
        </div>
        <div class="footer">
          <p>This is an automated notification from the University Placement Portal.
             Please do not reply to this email.</p>
        </div>
      </div>
    </body>
    </html>
    """
