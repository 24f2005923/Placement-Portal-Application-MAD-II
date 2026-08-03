import csv
import logging
import os
from datetime import datetime, timezone

from celery_app import celery
from models import db
from models.user import User

logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.monthly_reports.generate_monthly_report',
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def generate_monthly_report(self, target_year=None, target_month=None, requested_by_email=None):
    """
    Generate the monthly placement activity report as CSV.

    The report is used by both the admin-triggered endpoint and Celery Beat.
    It writes into EXPORTS_FOLDER so downloads use the existing CSV export
    workflow at /api/admin/export/download/<filename>.
    """
    logger.info('Monthly activity report task started: task_id=%s', self.request.id)

    try:
        from flask import current_app
        from services.admin_service import AdminService
        from services.email_service import send_email

        year, month = _resolve_report_period(target_year, target_month)
        report = AdminService.get_monthly_activity_report(year, month)

        exports_dir = current_app.config['EXPORTS_FOLDER']
        os.makedirs(exports_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"monthly_activity_report_{report['period_key']}_{timestamp}.csv"
        filepath = os.path.join(exports_dir, filename)

        _write_report_csv(filepath, report)

        recipients = _resolve_recipients(requested_by_email)
        emailed = 0
        for recipient in recipients:
            if send_email(
                to=recipient,
                subject=f"Monthly Placement Activity Report - {report['period']}",
                body_html=_email_body(report, filename),
                attachments=[filepath],
            ):
                emailed += 1

        metrics = report['metrics']
        return {
            'status': 'completed',
            'filename': filename,
            'filepath': filepath,
            'download_url': f'/api/admin/export/download/{filename}',
            'month': report['month'],
            'month_name': report['month_name'],
            'year': report['year'],
            'period': report['period'],
            'placement_drives_conducted': metrics['placement_drives_conducted'],
            'students_applied': metrics['students_applied'],
            'students_selected': metrics['students_selected'],
            'emails_sent': emailed,
            'recipients': recipients,
        }

    except Exception as exc:
        logger.error('Monthly activity report task failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


def _resolve_report_period(target_year, target_month):
    if target_year and target_month:
        return int(target_year), int(target_month)

    today = datetime.now(timezone.utc)
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def _write_report_csv(filepath, report):
    metrics = report['metrics']
    headers = [
        'Month',
        'Year',
        'Placement Drives Conducted',
        'Students Applied',
        'Students Selected',
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerow({
            'Month': report['month_name'],
            'Year': report['year'],
            'Placement Drives Conducted': metrics['placement_drives_conducted'],
            'Students Applied': metrics['students_applied'],
            'Students Selected': metrics['students_selected'],
        })


def _resolve_recipients(requested_by_email):
    if requested_by_email:
        return [requested_by_email]

    admin_rows = (
        db.session.query(User.email)
        .filter(User.role == 'admin', User.status == 'active')
        .all()
    )
    return [row.email for row in admin_rows if row.email]


def _email_body(report, filename):
    metrics = report['metrics']
    return f"""
    <p>Dear Admin,</p>
    <p>The monthly placement activity report for <strong>{report['period']}</strong> has been generated.</p>
    <table cellpadding="6" cellspacing="0" border="1">
      <tr><th align="left">Metric</th><th align="right">Value</th></tr>
      <tr><td>Placement Drives Conducted</td><td align="right">{metrics['placement_drives_conducted']}</td></tr>
      <tr><td>Students Applied</td><td align="right">{metrics['students_applied']}</td></tr>
      <tr><td>Students Selected</td><td align="right">{metrics['students_selected']}</td></tr>
    </table>
    <p>The CSV report is attached as <strong>{filename}</strong>.</p>
    """
