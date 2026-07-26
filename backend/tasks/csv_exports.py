"""
csv_exports.py — Async CSV export Celery tasks
───────────────────────────────────────────────
Provides two asynchronous tasks for exporting data as CSV files:

  • export_students_csv  — exports all student records with their
                           profile and application history
  • export_companies_csv — exports all company records with their
                           drive and placement statistics

Workflow:
  1. Admin triggers export via POST /api/admin/export/students
  2. Route enqueues the Celery task and returns a task_id immediately
  3. Task runs in the background and writes the CSV to backend/exports/
  4. Admin polls GET /api/admin/export/status/<task_id> until done
  5. Admin downloads the file via GET /api/admin/export/download/<filename>
  6. A completion email is sent to the requesting admin

Retry policy:
  • Retries up to 3 times with a 2-minute delay between attempts.
"""

import csv
import io
import logging
import os
from datetime import datetime, timezone

from celery_app import celery
from models import db
from models.student import Student
from models.company import Company
from models.application import Application
from models.user import User

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Student CSV Export
# ─────────────────────────────────────────────────────────────────

@celery.task(
    name='tasks.csv_exports.export_students_csv',
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def export_students_csv(self, requested_by_email: str = None):
    """
    Export all student records to a CSV file.

    Each row contains: student profile fields, user account details,
    application counts (total / selected / rejected), and
    current placement status.

    Args:
        requested_by_email: Admin email address to send completion
                            notification to.  Optional.

    Returns:
        Dict with file path, filename, row count, and download URL.
    """
    logger.info('=== Student CSV Export Task Started (task_id=%s) ===', self.request.id)

    try:
        from flask import current_app

        # ── Ensure exports directory exists ───────────────────────
        exports_dir = current_app.config['EXPORTS_FOLDER']
        os.makedirs(exports_dir, exist_ok=True)

        # ── Build filename with timestamp ─────────────────────────
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename  = f'students_export_{timestamp}.csv'
        filepath  = os.path.join(exports_dir, filename)

        # ── Query all students with eager loading ─────────────────
        students = (
            db.session.query(Student)
            .join(User, Student.user_id == User.id)
            .all()
        )

        # ── Write CSV ─────────────────────────────────────────────
        headers = [
            'ID', 'Name', 'Email', 'Register Number', 'Department',
            'Year', 'CGPA', 'Skills', 'Phone', 'Graduation Year',
            'Marks 10th', 'Marks 12th', 'Backlogs', 'Preferred Role',
            'Placement Status', 'Account Status',
            'Total Applications', 'Shortlisted', 'Interview Stage',
            'Selected', 'Rejected',
        ]

        row_count = 0
        with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            for student in students:
                user = student.user
                if user is None:
                    continue

                app_counts = _count_applications_by_status(student.applications)

                writer.writerow({
                    'ID':                   student.id,
                    'Name':                 user.name,
                    'Email':                user.email,
                    'Register Number':      student.register_number,
                    'Department':           student.department,
                    'Year':                 student.year,
                    'CGPA':                 student.cgpa,
                    'Skills':               ', '.join(student.get_skills()),
                    'Phone':                student.phone or '',
                    'Graduation Year':      student.graduation_year or '',
                    'Marks 10th':           student.marks_10th or '',
                    'Marks 12th':           student.marks_12th or '',
                    'Backlogs':             student.backlogs or 0,
                    'Preferred Role':       student.preferred_role or '',
                    'Placement Status':     student.placement_status,
                    'Account Status':       user.status,
                    'Total Applications':   app_counts['total'],
                    'Shortlisted':          app_counts['shortlisted'],
                    'Interview Stage':      app_counts['interview'],
                    'Selected':             app_counts['selected'],
                    'Rejected':             app_counts['rejected'],
                })
                row_count += 1

        logger.info('Student CSV export done: %d rows written to %s', row_count, filepath)

        # ── Send completion notification ───────────────────────────
        if requested_by_email:
            _send_export_notification(
                to=requested_by_email,
                export_type='Student',
                filename=filename,
                row_count=row_count,
            )

        return {
            'status': 'completed',
            'filename': filename,
            'filepath': filepath,
            'rows_exported': row_count,
            'export_type': 'students',
        }

    except Exception as exc:
        logger.error('Student CSV export failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────────────────────────
# Company CSV Export
# ─────────────────────────────────────────────────────────────────

@celery.task(
    name='tasks.csv_exports.export_companies_csv',
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def export_companies_csv(self, requested_by_email: str = None):
    """
    Export all company records to a CSV file.

    Each row includes: company profile, contact details, approval
    status, total drives created, and selection statistics.

    Args:
        requested_by_email: Admin email to notify on completion.

    Returns:
        Dict with file path, filename, row count, and download URL.
    """
    logger.info('=== Company CSV Export Task Started (task_id=%s) ===', self.request.id)

    try:
        from flask import current_app

        exports_dir = current_app.config['EXPORTS_FOLDER']
        os.makedirs(exports_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename  = f'companies_export_{timestamp}.csv'
        filepath  = os.path.join(exports_dir, filename)

        companies = (
            db.session.query(Company)
            .join(User, Company.user_id == User.id)
            .all()
        )

        headers = [
            'ID', 'Company Name', 'Industry', 'Website', 'City',
            'Contact Person', 'Contact Email', 'Contact Phone',
            'Approval Status', 'Blacklisted', 'Account Status',
            'Total Drives', 'Total Applications Received',
            'Total Shortlisted', 'Total Selected',
        ]

        row_count = 0
        with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            for company in companies:
                user = company.user
                if user is None:
                    continue

                # Tally application stats across all drives
                total_apps      = 0
                total_shortlist = 0
                total_selected  = 0

                for drive in company.drives:
                    for app in drive.applications:
                        total_apps += 1
                        if app.application_status in ('shortlisted', 'interview', 'selected'):
                            total_shortlist += 1
                        if app.application_status == 'selected':
                            total_selected += 1

                writer.writerow({
                    'ID':                         company.id,
                    'Company Name':               company.company_name,
                    'Industry':                   company.industry or '',
                    'Website':                    company.website or '',
                    'City':                       company.city or '',
                    'Contact Person':             company.contact_person or '',
                    'Contact Email':              company.contact_email or '',
                    'Contact Phone':              company.contact_phone or '',
                    'Approval Status':            company.approval_status,
                    'Blacklisted':                'Yes' if company.blacklisted else 'No',
                    'Account Status':             user.status,
                    'Total Drives':               len(company.drives),
                    'Total Applications Received': total_apps,
                    'Total Shortlisted':          total_shortlist,
                    'Total Selected':             total_selected,
                })
                row_count += 1

        logger.info('Company CSV export done: %d rows written to %s', row_count, filepath)

        if requested_by_email:
            _send_export_notification(
                to=requested_by_email,
                export_type='Company',
                filename=filename,
                row_count=row_count,
            )

        return {
            'status': 'completed',
            'filename': filename,
            'filepath': filepath,
            'rows_exported': row_count,
            'export_type': 'companies',
        }

    except Exception as exc:
        logger.error('Company CSV export failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


# ── Shared helpers ────────────────────────────────────────────────

def _count_applications_by_status(applications) -> dict:
    """
    Return a dictionary of application counts keyed by status.

    Args:
        applications: List of Application model objects.

    Returns:
        Dict with keys: total, applied, shortlisted, interview, selected, rejected.
    """
    counts = {
        'total': 0,
        'applied': 0,
        'shortlisted': 0,
        'interview': 0,
        'selected': 0,
        'rejected': 0,
    }
    for app in applications:
        counts['total'] += 1
        status = app.application_status
        if status in counts:
            counts[status] += 1
    return counts


def _send_export_notification(to: str, export_type: str, filename: str, row_count: int):
    """
    Send an email notification when an export has completed.

    Args:
        to:          Recipient email address.
        export_type: Human-readable type label ('Student' or 'Company').
        filename:    Name of the generated CSV file.
        row_count:   Number of rows exported.
    """
    from services.email_service import send_email

    subject = f'{export_type} Data Export Completed — {filename}'
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body        {{ font-family: Arial, sans-serif; color: #333; background: #f5f5f5; margin: 0; }}
        .container  {{ max-width: 560px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
        .header     {{ background: #4f46e5; color: #fff; padding: 24px 30px; }}
        .header h2  {{ margin: 0; font-size: 20px; }}
        .body       {{ padding: 24px 30px; }}
        .info-box   {{ background: #f0f0ff; border-left: 4px solid #4f46e5; padding: 14px 18px; border-radius: 4px; margin: 18px 0; }}
        .info-box p {{ margin: 4px 0; font-size: 14px; }}
        .footer     {{ background: #f9f9f9; padding: 14px 30px; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header"><h2>✅ Export Completed</h2></div>
        <div class="body">
          <p>Your <strong>{export_type}</strong> data export has finished successfully.</p>
          <div class="info-box">
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Records exported:</strong> {row_count}</p>
          </div>
          <p>Log into the Placement Portal admin panel to download the file.</p>
        </div>
        <div class="footer">
          <p>Automated notification — University Placement Portal</p>
        </div>
      </div>
    </body>
    </html>
    """
    send_email(to=to, subject=subject, body_html=body_html)
