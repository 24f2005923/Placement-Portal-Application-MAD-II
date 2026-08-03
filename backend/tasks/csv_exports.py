import logging

from celery_app import celery
from models import db
from models.application import Application
from models.company import Company
from models.student import Student
from models.user import User
from services.company_service import CompanyService
from services.student_service import StudentService
from utils.csv_export import (
    export_path,
    export_result,
    send_export_notification,
    timestamped_csv_name,
    write_summary_table_csv,
    write_table_csv,
)

logger = logging.getLogger(__name__)


@celery.task(name='tasks.csv_exports.export_student_applications_csv', bind=True, max_retries=3, default_retry_delay=120)
def export_student_applications_csv(self, user_id: int, requested_by_email: str = None):
    logger.info('Student applications CSV export started: task_id=%s user_id=%s', self.request.id, user_id)
    try:
        student = StudentService.get_student_by_user(user_id)
        rows = StudentService.get_application_export_rows(user_id)
        filename = timestamped_csv_name(f'student_applications_{student.id}')
        filepath = export_path(filename)

        write_table_csv(filepath, [
            'Student ID',
            'Company Name',
            'Drive Title',
            'Application Status',
            'Application Date',
        ], rows)

        row_count = len(rows)
        if requested_by_email:
            send_export_notification(
                requested_by_email,
                'Application History',
                filename,
                row_count,
                audience='student',
            )

        return export_result(filename, filepath, row_count, 'student_applications', student_id=student.id)
    except Exception as exc:
        logger.error('Student applications CSV export failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


@celery.task(name='tasks.csv_exports.export_company_drive_applications_csv', bind=True, max_retries=3, default_retry_delay=120)
def export_company_drive_applications_csv(self, user_id: int, drive_id: int, requested_by_email: str = None):
    logger.info('Company drive applications CSV export started: task_id=%s user_id=%s drive_id=%s', self.request.id, user_id, drive_id)
    try:
        export_data = CompanyService.get_drive_application_export(user_id, drive_id)
        filename = timestamped_csv_name(
            f"company_drive_applications_{export_data['company_id']}_{export_data['drive_id']}"
        )
        filepath = export_path(filename)

        write_summary_table_csv(
            filepath,
            [
                ('Drive Title', export_data['drive_title']),
                ('Company Name', export_data['company_name']),
                ('Total Applications', export_data['total_applications']),
                ('Export Generated Date & Time', export_data['generated_at']),
            ],
            [
                'Drive ID',
                'Drive Title',
                'Company Name',
                'Student ID',
                'Student Name',
                'Student Email',
                'Department',
                'Application Status',
                'Applied Date',
            ],
            export_data['rows'],
        )

        row_count = export_data['total_applications']
        if requested_by_email:
            send_export_notification(
                requested_by_email,
                'Drive Applications',
                filename,
                row_count,
                audience='company',
            )

        return export_result(
            filename,
            filepath,
            row_count,
            'company_drive_applications',
            company_id=export_data['company_id'],
            drive_id=export_data['drive_id'],
        )
    except Exception as exc:
        logger.error('Company drive applications CSV export failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


@celery.task(name='tasks.csv_exports.export_students_csv', bind=True, max_retries=3, default_retry_delay=120)
def export_students_csv(self, requested_by_email: str = None):
    logger.info('Student CSV export started: task_id=%s', self.request.id)
    try:
        filename = timestamped_csv_name('students_export')
        filepath = export_path(filename)

        students = db.session.query(Student).join(User, Student.user_id == User.id).all()
        rows = [_student_export_row(student) for student in students if student.user]
        write_table_csv(filepath, STUDENT_EXPORT_HEADERS, rows)

        row_count = len(rows)
        if requested_by_email:
            send_export_notification(requested_by_email, 'Student', filename, row_count)

        return export_result(filename, filepath, row_count, 'students')
    except Exception as exc:
        logger.error('Student CSV export failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


@celery.task(name='tasks.csv_exports.export_companies_csv', bind=True, max_retries=3, default_retry_delay=120)
def export_companies_csv(self, requested_by_email: str = None):
    logger.info('Company CSV export started: task_id=%s', self.request.id)
    try:
        filename = timestamped_csv_name('companies_export')
        filepath = export_path(filename)

        companies = db.session.query(Company).join(User, Company.user_id == User.id).all()
        rows = [_company_export_row(company) for company in companies if company.user]
        write_table_csv(filepath, COMPANY_EXPORT_HEADERS, rows)

        row_count = len(rows)
        if requested_by_email:
            send_export_notification(requested_by_email, 'Company', filename, row_count)

        return export_result(filename, filepath, row_count, 'companies')
    except Exception as exc:
        logger.error('Company CSV export failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


STUDENT_EXPORT_HEADERS = [
    'ID', 'Name', 'Email', 'Register Number', 'Department',
    'Year', 'CGPA', 'Skills', 'Phone', 'Graduation Year',
    'Marks 10th', 'Marks 12th', 'Backlogs', 'Preferred Role',
    'Placement Status', 'Account Status',
    'Total Applications', 'Shortlisted', 'Interview Stage',
    'Selected', 'Rejected',
]

COMPANY_EXPORT_HEADERS = [
    'ID', 'Company Name', 'Industry', 'Website', 'City',
    'Contact Person', 'Contact Email', 'Contact Phone',
    'Approval Status', 'Blacklisted', 'Account Status',
    'Total Drives', 'Total Applications Received',
    'Total Shortlisted', 'Total Selected',
]


def _student_export_row(student):
    counts = _count_applications_by_status(student.applications)
    return {
        'ID': student.id,
        'Name': student.user.name,
        'Email': student.user.email,
        'Register Number': student.register_number,
        'Department': student.department,
        'Year': student.year,
        'CGPA': student.cgpa,
        'Skills': ', '.join(student.get_skills()),
        'Phone': student.phone or '',
        'Graduation Year': student.graduation_year or '',
        'Marks 10th': student.marks_10th or '',
        'Marks 12th': student.marks_12th or '',
        'Backlogs': student.backlogs or 0,
        'Preferred Role': student.preferred_role or '',
        'Placement Status': student.placement_status,
        'Account Status': student.user.status,
        'Total Applications': counts['total'],
        'Shortlisted': counts['shortlisted'],
        'Interview Stage': counts['interview'],
        'Selected': counts['selected'],
        'Rejected': counts['rejected'],
    }


def _company_export_row(company):
    app_counts = _company_application_counts(company)
    return {
        'ID': company.id,
        'Company Name': company.company_name,
        'Industry': company.industry or '',
        'Website': company.website or '',
        'City': company.city or '',
        'Contact Person': company.contact_person or '',
        'Contact Email': company.contact_email or '',
        'Contact Phone': company.contact_phone or '',
        'Approval Status': company.approval_status,
        'Blacklisted': 'Yes' if company.blacklisted else 'No',
        'Account Status': company.user.status,
        'Total Drives': len(company.drives),
        'Total Applications Received': app_counts['total'],
        'Total Shortlisted': app_counts['shortlisted'],
        'Total Selected': app_counts['selected'],
    }


def _company_application_counts(company):
    counts = {'total': 0, 'shortlisted': 0, 'selected': 0}
    for drive in company.drives:
        for application in drive.applications:
            counts['total'] += 1
            if application.application_status in ('shortlisted', 'interview', 'selected'):
                counts['shortlisted'] += 1
            if application.application_status == 'selected':
                counts['selected'] += 1
    return counts


def _count_applications_by_status(applications):
    counts = {
        'total': 0,
        'applied': 0,
        'shortlisted': 0,
        'interview': 0,
        'selected': 0,
        'rejected': 0,
    }
    for application in applications:
        counts['total'] += 1
        status = application.application_status
        if status in counts:
            counts[status] += 1
    return counts
