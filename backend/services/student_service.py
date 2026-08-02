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
        from models.company import Company
        student = cls.get_student_by_user(user_id)
        query = db.session.query(PlacementDrive).join(Company).filter(PlacementDrive.status == 'open')

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
        current_date = datetime.now().strftime('%B %d, %Y')

        html_doc = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Placement Offer Letter - {company_name}</title>
  <style>
    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 40px; color: #222; background-color: #fff; line-height: 1.6; }}
    .header {{ border-bottom: 3px solid #0d6efd; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
    .company-name {{ font-size: 26px; font-weight: bold; color: #0d6efd; }}
    .doc-title {{ font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #555; text-align: right; }}
    .meta-table {{ width: 100%; margin-bottom: 30px; border-collapse: collapse; }}
    .meta-table td {{ padding: 6px 0; font-size: 14px; }}
    .content {{ font-size: 15px; margin-bottom: 40px; }}
    .highlight {{ background-color: #eef2ff; border-left: 4px solid #0d6efd; padding: 15px; margin: 20px 0; border-radius: 4px; }}
    .footer {{ border-top: 1px solid #ddd; padding-top: 20px; margin-top: 50px; font-size: 12px; color: #777; display: flex; justify-content: space-between; }}
    .signature {{ margin-top: 50px; display: flex; justify-content: space-between; }}
    .sig-block {{ text-align: center; width: 220px; border-top: 1px solid #333; padding-top: 8px; font-size: 14px; font-weight: bold; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="company-name">{company_name}</div>
      <div style="font-size: 13px; color: #555; margin-top: 4px;">In Association with University Placement Cell</div>
    </div>
    <div class="doc-title">OFFICIAL PLACEMENT CONFIRMATION</div>
  </div>

  <table class="meta-table">
    <tr><td><strong>Date:</strong> {current_date}</td><td style="text-align: right;"><strong>Ref No:</strong> OFF-{app.id:06d}</td></tr>
    <tr><td><strong>Candidate Name:</strong> {student_name}</td><td style="text-align: right;"><strong>Register No:</strong> {reg_num}</td></tr>
    <tr><td><strong>Department:</strong> {dept}</td><td style="text-align: right;"><strong>Applied Date:</strong> {applied_date}</td></tr>
  </table>

  <div class="content">
    <p>Dear <strong>{student_name}</strong>,</p>
    <p>We are pleased to inform you that following your evaluation during the campus placement drive conducted by the University Placement Cell, <strong>{company_name}</strong> is delighted to offer you employment for the position of <strong>{job_role}</strong>.</p>
    
    <div class="highlight">
      <strong>Offer Summary Details:</strong><br/>
      • <strong>Designation:</strong> {job_role}<br/>
      • <strong>Compensation Package:</strong> {package_val}<br/>
      • <strong>Placement Status:</strong> Confirmed & Placed<br/>
      • <strong>Organization:</strong> {company_name}
    </div>

    <p>Your technical proficiency, problem-solving capabilities, and academic accomplishments impressed our selection panel. Official joining instructions and onboarding documentation will be delivered to your registered email address.</p>
    
    <p>We congratulate you on this milestone and look forward to your contributions at <strong>{company_name}</strong>.</p>
  </div>

  <div class="signature">
    <div class="sig-block">Head of Campus Recruitment<br/><span style="font-weight: normal; font-size: 12px;">{company_name}</span></div>
    <div class="sig-block">Director of Placements<br/><span style="font-weight: normal; font-size: 12px;">University Placement Cell</span></div>
  </div>

  <div class="footer">
    <span>Issued via University Placement Portal</span>
    <span>Document Verification Code: VERIFIED-OFFER-{app.id}</span>
  </div>
</body>
</html>"""
        clean_company = "".join(c for c in company_name if c.isalnum() or c == '_')
        clean_student = "".join(c for c in student_name if c.isalnum() or c == '_')
        return html_doc, f"Offer_Letter_{clean_company}_{clean_student}.html"
