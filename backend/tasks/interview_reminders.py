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

from sqlalchemy.exc import IntegrityError

from celery_app import celery
from models import db
from models.interview import Interview
from models.application import Application
from models.student import Student
from models.interview_reminder_history import InterviewReminderHistory
from services.email_service import send_email
from services.gchat_service import send_gchat_message
from services.sms_service import get_sms_provider
from utils.email_templates import EmailTemplateBuilder

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

            # ── Idempotency guard ─────────────────────────────────
            # Check whether a reminder has already been dispatched for
            # this specific interview. If so, skip it entirely to avoid
            # spamming the student even if the Beat task fires multiple
            # times on the same day.
            already_notified = (
                db.session.query(InterviewReminderHistory)
                .filter(
                    InterviewReminderHistory.student_id  == student.id,
                    InterviewReminderHistory.interview_id == interview.id,
                )
                .first()
            )
            if already_notified:
                logger.debug(
                    'Skipping duplicate reminder for student_id=%s interview_id=%s (sent at %s)',
                    student.id, interview.id, already_notified.sent_at
                )
                continue

            # Build human-readable interview details.
            interview_info = _build_interview_info(interview, application)

            # ── 1. Email reminder ─────────────────────────────────
            email_subject = f"Interview Reminder: {interview_info['company']} — {interview_info['interview_date']}"
            email_body    = EmailTemplateBuilder.build_interview_reminder_from_info(user.name, interview_info)
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

            # ── Record to history (idempotency write) ─────────────
            # Use try/except to gracefully handle the rare race condition
            # where two workers dispatch simultaneously for the same record.
            try:
                history_entry = InterviewReminderHistory(
                    student_id=student.id,
                    interview_id=interview.id,
                )
                db.session.add(history_entry)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logger.warning(
                    'Duplicate reminder history write for student_id=%s interview_id=%s — skipped.',
                    student.id, interview.id
                )

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


