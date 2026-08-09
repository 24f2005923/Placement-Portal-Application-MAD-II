
import logging
from celery_app import celery
from models import db
from models.user import User
from services.email_service import send_bulk_emails
from utils.email_templates import EmailTemplateBuilder

logger = logging.getLogger(__name__)


@celery.task(name='tasks.announcements.send_mass_announcement')
def send_mass_announcement(subject: str, body_html: str, target_role: str = 'student'):
    
    logger.info('=== Mass Announcement Task Started (Target: %s) ===', target_role)

    
    users = db.session.query(User).filter_by(role=target_role, status='active').all()
    if not users:
        logger.info('No active %s users found. Task done.', target_role)
        return {'status': 'completed', 'sent': 0}

    recipients = [u.email for u in users if u.email]
    
    
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
    
    subject = "🎓 Placement Portal — Weekly Login Reminder"
    body_html = EmailTemplateBuilder.build_weekly_login_reminder()
    
    # Call the generic mass email task synchronously
    return send_mass_announcement(subject=subject, body_html=body_html, target_role='student')
