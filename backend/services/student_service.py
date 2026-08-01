from models import db
from models.student import Student
from models.placement_drive import PlacementDrive
from models.application import Application
from exceptions import NotFound, ValidationError, Conflict
from services.file_service import save_resume, delete_resume
from utils.stats import create_stat_item

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
        open_drives = db.session.query(PlacementDrive).filter(PlacementDrive.status == 'open').count()
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
        student = cls.get_student_by_user(user_id)
        
        if 'name' in payload:
            student.user.name = payload['name']
        if 'email' in payload:
            student.user.email = payload['email'].lower().strip()

        fields_list = ['department', 'year', 'cgpa', 'phone', 'address',
                       'marks_10th', 'marks_12th', 'backlogs', 'graduation_year', 'preferred_role']
                       
        for key in fields_list:
            if key in payload:
                setattr(student, key, payload[key])

        if 'skills' in payload:
            student.save_skills(payload['skills'])

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
        student = cls.get_student_by_user(user_id)
        query = db.session.query(PlacementDrive).filter(PlacementDrive.status == 'open')

        if search_query:
            wildcard = f"%{search_query}%"
            query = query.filter(
                db.or_(
                    PlacementDrive.job_role.ilike(wildcard),
                    PlacementDrive.title.ilike(wildcard)
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
        drive = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
        if not drive:
            raise NotFound('Placement drive not found')
            
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
        drive = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
        if not drive:
            raise NotFound('Placement drive not found')

        if drive.status != 'open':
            raise ValidationError('This drive is not accepting applications right now')

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
    def get_my_interviews(cls, user_id):
        student = cls.get_student_by_user(user_id)
        interview_apps = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.application_status == 'interview'
        ).all()

        return [
            {
                **app.interview.to_dict(),
                'drive_title': app.drive.title if app.drive else '',
                'company_name': app.drive.company.company_name if app.drive and app.drive.company else ''
            }
            for app in interview_apps if app.interview
        ]

    @classmethod
    def get_placement_history(cls, user_id):
        student = cls.get_student_by_user(user_id)
        selections = db.session.query(Application).filter(
            Application.student_id == student.id,
            Application.application_status == 'selected'
        ).all()

        return [
            {
                'company': app.drive.company.company_name if app.drive and app.drive.company else '',
                'role': app.drive.job_role if app.drive else '',
                'year': app.applied_at.year if app.applied_at else '',
                'package': app.drive.package if app.drive else '',
                'drive_title': app.drive.title if app.drive else ''
            }
            for app in selections
        ]
