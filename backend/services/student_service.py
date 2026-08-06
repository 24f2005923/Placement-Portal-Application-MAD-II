from models import db
from models.student import Student
from models.placement_drive import PlacementDrive
from models.application import Application
from exceptions import NotFound, ValidationError, Conflict
from services.file_service import save_resume, delete_resume
from utils.stats import create_stat_item
from utils.repository import BaseRepository
from utils.email_templates import EmailTemplateBuilder
from utils.student_updater import apply_student_profile_fields

class StudentService:
    """Service layer handling student workflows and application tracking."""
    
    @staticmethod
    def get_student_by_user(user_id):
        student = db.session.query(Student).filter(Student.user_id == int(user_id)).first()
        if not student:
            raise NotFound('Student not found')
        return student

    @classmethod
    def get_stats(cls, user_id):
        student = cls.get_student_by_user(user_id)
        open_drives = PlacementDrive.student_visible_query().count()
        applied_drives = db.session.query(Application).filter(Application.student_id == student.id).count()
        interviews = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.application_status == 'interview'
        ).count()

        return [
            create_stat_item('Available Drives', open_drives, 'bi-briefcase', 'primary'),
            create_stat_item('Applied Drives', applied_drives, 'bi-send-check', 'success'),
            create_stat_item('Interview Schedule', interviews, 'bi-calendar-event', 'warning'),
            create_stat_item('Placement Status', student.placement_status, 'bi-emoji-smile', 'danger')
        ]

    @classmethod
    def get_profile(cls, user_id):
        student = cls.get_student_by_user(user_id)
        return student.to_dict()

    @classmethod
    def update_profile(cls, user_id, payload):
        """Update a student's own profile from their request payload."""
        student = cls.get_student_by_user(user_id)
        apply_student_profile_fields(student, payload)
        db.session.commit()
        return student.to_dict()

    @classmethod
    def upload_resume(cls, user_id, file_obj):
        student = cls.get_student_by_user(user_id)
        previous_resume = student.resume_path

        saved_filename, error_msg = save_resume(file_obj, student.id)
        if error_msg:
            raise ValidationError(error_msg)

        student.resume_path = saved_filename
        db.session.commit()

        if previous_resume and previous_resume != saved_filename:
            delete_resume(previous_resume)

        return saved_filename

    @classmethod
    def list_open_drives(cls, user_id, search_query):
        from models.company import Company
        student = cls.get_student_by_user(user_id)
        query = PlacementDrive.student_visible_query()

        clean_search = str(search_query or '').strip()
        if clean_search:
            wildcard = f"%{clean_search}%"
            query = query.filter(
                db.or_(
                    PlacementDrive.job_role.ilike(wildcard),
                    PlacementDrive.title.ilike(wildcard),
                    PlacementDrive.eligibility.ilike(wildcard),
                    PlacementDrive.package.ilike(wildcard),
                    Company.company_name.ilike(wildcard)
                )
            )

        all_drives = query.order_by(PlacementDrive.created_at.desc()).all()
        applied_ids = {app.drive_id for app in student.applications}

        return [
            {**drive.to_dict(), 'already_applied': drive.id in applied_ids}
            for drive in all_drives
        ]

    @classmethod
    def get_drive_details(cls, user_id, drive_id):
        student = cls.get_student_by_user(user_id)
        drive = BaseRepository.first_or_404(
            PlacementDrive.student_visible_query().filter(PlacementDrive.id == drive_id),
            'Placement drive not found',
        )
            
        drive_dict = drive.to_dict()
        user_app = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.drive_id == drive_id
        ).first()
        
        drive_dict['already_applied'] = user_app is not None
        if user_app:
            drive_dict['application'] = user_app.to_dict(include_student=False)

        return drive_dict

    @classmethod
    def apply_for_drive(cls, user_id, drive_id, cover_note, resume_file=None):
        student = cls.get_student_by_user(user_id)
        drive = BaseRepository.get_by_id_or_404(PlacementDrive, drive_id, 'Placement drive not found')

        if not drive.is_accepting_applications:
            raise ValidationError('This placement drive is closed and is no longer accepting applications.')

        duplicate_app = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.drive_id == drive_id
        ).first()
        
        if duplicate_app:
            raise Conflict('You already applied for this drive')

        saved_resume = None
        if resume_file:
            saved_resume, error_msg = save_resume(resume_file, student.id)
            if error_msg:
                raise ValidationError(error_msg)
            student.resume_path = saved_resume

        new_app = Application(
            student_id=student.id,
            drive_id=drive_id,
            cover_note=cover_note,
            resume_path=saved_resume or student.resume_path,
            application_status='applied'
        )
        db.session.add(new_app)

        if student.placement_status == 'Not Placed':
            student.placement_status = 'Applied'

        db.session.commit()
        return new_app.to_dict()

    @classmethod
    def get_my_applications(cls, user_id):
        student = cls.get_student_by_user(user_id)
        apps = db.session.query(Application).filter(
            Application.student_id == student.id
        ).order_by(Application.applied_at.desc()).all()
        return [app.to_dict(include_student=False) for app in apps]

    @classmethod
    def get_application_export_rows(cls, user_id):
        student = cls.get_student_by_user(user_id)
        apps = db.session.query(Application).filter(
            Application.student_id == student.id
        ).order_by(Application.applied_at.desc()).all()

        return [
            {
                'Student ID': student.id,
                'Company Name': app.drive.company.company_name if app.drive and app.drive.company else '',
                'Drive Title': app.drive.title if app.drive else '',
                'Application Status': app.application_status,
                'Application Date': app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else '',
            }
            for app in apps
        ]

    @classmethod
    def get_my_interviews(cls, user_id):
        student = cls.get_student_by_user(user_id)
        interview_apps = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.application_status.in_(['interview', 'shortlisted'])
        ).all()

        interviews_list = []
        for app in interview_apps:
            if app.interview:
                interviews_list.append({
                    **app.interview.to_dict(),
                    'application_id': app.id,
                    'drive_title': app.drive.title if app.drive else '',
                    'job_role': app.drive.job_role if app.drive else '',
                    'company_name': app.drive.company.company_name if app.drive and app.drive.company else '',
                    'remarks': app.interview.remarks or (app.result.remarks if app.result else '')
                })
        return interviews_list

    @classmethod
    def get_placement_history(cls, user_id):
        student = cls.get_student_by_user(user_id)
        selections = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.application_status == 'selected'
        ).all()

        return [
            {
                'application_id': app.id,
                'company': app.drive.company.company_name if app.drive and app.drive.company else '',
                'role': app.drive.job_role if app.drive else '',
                'year': app.applied_at.year if app.applied_at else '',
                'package': app.drive.package if app.drive else '',
                'drive_title': app.drive.title if app.drive else '',
                'remarks': app.result.remarks if app.result else ''
            }
            for app in selections
        ]

    @classmethod
    def generate_offer_letter(cls, user_id, app_id):
        from datetime import datetime
        student = cls.get_student_by_user(user_id)
        app = db.session.query(Application).filter(
            Application.id == app_id,
            Application.student_id == student.id
        ).first()

        if not app:
            raise NotFound('Application not found')

        if app.application_status != 'selected':
            raise ValidationError('Offer letter is only available for selected/placed candidates.')

        student_name = student.user.name if student.user else 'Student'
        reg_num = student.register_number
        dept = student.department
        company_name = app.drive.company.company_name if app.drive and app.drive.company else 'Company'
        job_role = app.drive.job_role if app.drive else 'Software Engineer'
        package_val = app.drive.package if app.drive and app.drive.package else 'As per company policy'
        applied_date = app.applied_at.strftime('%B %d, %Y') if app.applied_at else 'Recent'

        html_doc, filename = EmailTemplateBuilder.build_offer_letter(
            student_name, reg_num, dept, company_name, job_role, package_val, applied_date, app.id
        )
        return html_doc, filename
