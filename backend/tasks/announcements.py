"""
announcements.py — General mass email tasks
─────────────────────────────────────────────
Contains Celery tasks for sending announcements to all students.
"""

import logging
from celery_app import celery
from models import db
from models.user import User
from services.email_service import send_bulk_emails

logger = logging.getLogger(__name__)


@celery.task(name='tasks.announcements.send_mass_announcement')
def send_mass_announcement(subject: str, body_html: str, target_role: str = 'student'):
    """
    Sends an arbitrary HTML email to all active users of a specific role.
    This can be triggered by an Admin from the frontend (if an API is added).
    """
    logger.info('=== Mass Announcement Task Started (Target: %s) ===', target_role)

    # Find all active users matching the role
    users = db.session.query(User).filter_by(role=target_role, status='active').all()
    if not users:
        logger.info('No active %s users found. Task done.', target_role)
        return {'status': 'completed', 'sent': 0}

    recipients = [u.email for u in users if u.email]
    
    # Use the existing bulk email helper
    results = send_bulk_emails(recipients, subject, body_html)
    
    logger.info('=== Mass Announcement Task Done ===')
    return {
        'status': 'completed',
        'target_role': target_role,
        'sent': results['sent'],
        'failed': results['failed']
    }


@celery.task(name='tasks.announcements.weekly_login_reminder')
def weekly_login_reminder():
    """
    Scheduled task that sends a standard "Reminder to Login" email
    to all active students.
    """
    subject = "🎓 Placement Portal — Weekly Login Reminder"
    
    body_html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body        { font-family: Arial, sans-serif; color: #333; background: #f5f5f5; margin: 0; padding: 0; }
        .container  { max-width: 600px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .header     { background: #4f46e5; color: #fff; padding: 28px 32px; text-align: center; }
        .header h1  { margin: 0; font-size: 22px; }
        .body       { padding: 28px 32px; }
        .body p     { line-height: 1.6; }
        .button     { display: inline-block; background: #4f46e5; color: #ffffff !important; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 15px; }
        .footer     { background: #f9f9f9; padding: 16px 32px; font-size: 12px; color: #888; border-top: 1px solid #eee; text-align: center; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Reminder to Login</h1>
        </div>
        <div class="body">
          <p>Hello Students!</p>
          <p>This is a friendly reminder to log in to the Placement Portal and check your dashboard. New placement drives or announcements may have been posted!</p>
          <p>Keeping your profile updated and checking regularly ensures you don't miss any deadlines.</p>
          <center>
            <a href="http://localhost:5173/login" class="button">Go to Placement Portal</a>
          </center>
        </div>
        <div class="footer">
          <p>This is an automated notification. Please do not reply to this email.</p>
        </div>
      </div>
    </body>
    </html>
    """
    
    # Call the generic mass email task synchronously
    return send_mass_announcement(subject=subject, body_html=body_html, target_role='student')
