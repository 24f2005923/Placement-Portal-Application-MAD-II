"""
drive_reminders.py — Daily placement drive deadline reminder Celery task
──────────────────────────────────────────────────────────────────────
This module defines a scheduled Celery task that runs every day
to identify open placement drives whose application deadline is within
the next 48 hours.

It determines eligible students (active students who have NOT already
applied) and sends them an email reminder.

To prevent duplicate emails, it logs each dispatched reminder into
the ReminderHistory table.

Retry policy:
  • Retries up to 3 times with a 5-minute delay between attempts.
"""

import logging
from datetime import date, timedelta

from celery_app import celery
from models import db
from models.placement_drive import PlacementDrive
from models.student import Student
from models.application import Application
from models.reminder_history import ReminderHistory
from services.email_service import send_email

logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.drive_reminders.send_drive_deadline_reminders',
    bind=True,
    max_retries=3,
    default_retry_delay=300,   # retry after 5 minutes
)
def send_drive_deadline_reminders(self):
    """
    Scheduled task: send placement drive deadline reminders to eligible students.

    Finds all 'open' drives with a deadline today or tomorrow.
    Finds active students who have not applied.
    Emails the students and records the action in ReminderHistory.
    """
    logger.info('=== Drive Deadline Reminder Task Started ===')

    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # 1. Find upcoming closing drives (deadline today or tomorrow)
        upcoming_drives = (
            db.session.query(PlacementDrive)
            .filter(
                PlacementDrive.status == 'open',
                PlacementDrive.deadline.isnot(None),
                PlacementDrive.deadline.in_([today, tomorrow])
            )
            .all()
        )

        if not upcoming_drives:
            logger.info('No upcoming drive deadlines found for %s / %s. Task done.', today, tomorrow)
            return {
                'status': 'completed',
                'reminders_sent': 0,
                'date_checked': str(today),
            }

        reminders_sent = 0

        for drive in upcoming_drives:
            # Gather all active students
            # Based on existing codebase logic, we'll fetch all students whose users are approved/active.
            # Then filter out those who have applied.
            from models.user import User
            
            all_students = (
                db.session.query(Student)
                .join(User, Student.user_id == User.id)
                .filter(User.status == 'active')
                .all()
            )

            for student in all_students:
                # Check if student already applied
                has_applied = db.session.query(Application).filter(
                    Application.student_id == student.id,
                    Application.drive_id == drive.id
                ).first() is not None

                if has_applied:
                    continue  # Already applied

                # Check if reminder was already sent
                already_reminded = db.session.query(ReminderHistory).filter(
                    ReminderHistory.student_id == student.id,
                    ReminderHistory.drive_id == drive.id
                ).first() is not None

                if already_reminded:
                    continue  # Already sent

                # Send email
                company_name = drive.company.company_name if drive.company else 'Unknown Company'
                subject = f"Deadline Approaching: Apply for {company_name} — {drive.job_role}"
                body = _build_drive_reminder_email(student.user.name, drive)
                
                email_sent = send_email(to=student.user.email, subject=subject, body_html=body)
                
                # Record in history if sent (or if simulated in console mode)
                if email_sent:
                    history_record = ReminderHistory(student_id=student.id, drive_id=drive.id)
                    db.session.add(history_record)
                    db.session.commit()
                    reminders_sent += 1
                    logger.info('Sent drive reminder to %s for drive %s', student.user.email, drive.id)

        logger.info('=== Drive Deadline Reminder Task Done: %d reminders sent ===', reminders_sent)
        return {
            'status': 'completed',
            'reminders_sent': reminders_sent,
            'date_checked': str(today),
        }

    except Exception as exc:
        logger.error('Drive deadline reminder task failed: %s', exc, exc_info=True)
        db.session.rollback()
        raise self.retry(exc=exc)


def _build_drive_reminder_email(student_name: str, drive: PlacementDrive) -> str:
    """
    Build an HTML email body for the drive deadline reminder.
    """
    company_name = drive.company.company_name if drive.company else 'Unknown Company'
    deadline_str = drive.deadline.strftime('%d %B %Y') if drive.deadline else 'TBD'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body        {{ font-family: Arial, sans-serif; color: #333; background: #f5f5f5; margin: 0; padding: 0; }}
        .container  {{ max-width: 600px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header     {{ background: #dc2626; color: #fff; padding: 28px 32px; }}
        .header h1  {{ margin: 0; font-size: 22px; }}
        .body       {{ padding: 28px 32px; }}
        .body p     {{ line-height: 1.6; }}
        .info-box   {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px 20px; border-radius: 4px; margin: 20px 0; }}
        .info-box p {{ margin: 6px 0; }}
        .footer     {{ background: #f9f9f9; padding: 16px 32px; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>⏳ Placement Drive Deadline Approaching</h1>
        </div>
        <div class="body">
          <p>Dear <strong>{student_name}</strong>,</p>
          <p>This is a quick reminder that the application deadline for an active placement drive is fast approaching. You have not submitted an application yet.</p>
          <div class="info-box">
            <p><strong>Company:</strong> {company_name}</p>
            <p><strong>Role:</strong> {drive.job_role}</p>
            <p><strong>Package:</strong> {drive.package or 'Not disclosed'}</p>
            <p><strong>Deadline:</strong> {deadline_str}</p>
          </div>
          <p>If you wish to be considered for this opportunity, please log in to your student dashboard and submit your application before the deadline.</p>
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
