import logging
from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError

from celery_app import celery
from models import db
from models.interview import Interview
from models.application import Application
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
    default_retry_delay=300,
)
def send_interview_reminders(self):
  
    logger.info('=== Interview Reminder Task Started ===')

    try:
        today    = date.today()
        tomorrow = today + timedelta(days=1)

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
            application = interview.application
            if application is None:
                continue

            student = application.student
            if student is None:
                continue

            user = student.user
            if user is None:
                continue

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

            interview_info = _build_interview_info(interview, application)

            email_subject = f"Interview Reminder: {interview_info['company']} — {interview_info['interview_date']}"
            email_body    = EmailTemplateBuilder.build_interview_reminder_from_info(user.name, interview_info)
            send_email(to=user.email, subject=email_subject, body_html=email_body)

            gchat_text = (
                f"🗓️ *Interview Reminder* — {user.name}\n"
                f"Company: {interview_info['company']}\n"
                f"Role: {interview_info['role']}\n"
                f"Date: {interview_info['interview_date']} at {interview_info['interview_time']}\n"
                f"Mode: {interview_info['mode']}"
            )
            send_gchat_message(gchat_text)

            if student.phone:
                sms_body = (
                    f"Hi {user.name}, your interview with {interview_info['company']} "
                    f"is on {interview_info['interview_date']} at {interview_info['interview_time']}. "
                    f"Mode: {interview_info['mode']}. All the best!"
                )
                sms_provider.send(to=student.phone, message=sms_body)

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
        db.session.rollback()
        raise self.retry(exc=exc)



def _build_interview_info(interview, application) -> dict:
   
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


