from datetime import date
from models import db
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.interview import Interview
from models.result import Result
from exceptions import NotFound, ValidationError, Forbidden
from utils.stats import create_stat_item
from utils.validators import validate_phone

class CompanyService:
    """Service layer handling company-specific logic, placement drives and interviews."""
    
    @staticmethod
    def get_company_by_user(user_id):
        company = db.session.query(Company).filter(Company.user_id == int(user_id)).first()
        if not company:
            raise NotFound('Company not found')
        return company

    @classmethod
    def get_stats(cls, user_id):
        company = cls.get_company_by_user(user_id)
        drive_ids = company.drive_ids
        total_drives = len(drive_ids)

        if total_drives > 0:
            total_applications = db.session.query(Application).filter(
                Application.drive_id.in_(drive_ids)
            ).count()
            
            shortlisted = db.session.query(Application).filter(
                Application.drive_id.in_(drive_ids),
                Application.application_status.in_(['shortlisted', 'interview', 'selected'])
            ).count()
            
            selected = db.session.query(Application).filter(
                Application.drive_id.in_(drive_ids),
                Application.application_status == 'selected'
            ).count()
        else:
            total_applications = 0
            shortlisted = 0
            selected = 0

        return [
            create_stat_item('Total Drives', total_drives, 'bi-megaphone', 'primary'),
            create_stat_item('Applications Received', total_applications, 'bi-inbox', 'success'),
            create_stat_item('Shortlisted Students', shortlisted, 'bi-person-check', 'warning'),
            create_stat_item('Selected Students', selected, 'bi-trophy', 'danger')
        ]

    @classmethod
    def get_profile(cls, user_id):
        company = cls.get_company_by_user(user_id)
        return company.to_dict()

    @classmethod
    def update_profile(cls, user_id, payload):
        company = cls.get_company_by_user(user_id)
        
        if 'contact_phone' in payload and payload['contact_phone']:
            payload['contact_phone'] = validate_phone(payload['contact_phone'], field_name="Contact phone")

        allowed_fields = ['company_name', 'industry', 'website', 'description',
                          'contact_person', 'contact_email', 'contact_phone', 'city', 'address']
                          
        for field in allowed_fields:
            if field in payload:
                setattr(company, field, payload[field])

        if 'name' in payload:
            company.user.name = payload['name']

        db.session.commit()
        return company.to_dict()

    @classmethod
    def get_drives(cls, user_id):
        company = cls.get_company_by_user(user_id)
        drives = db.session.query(PlacementDrive).filter(
            PlacementDrive.company_id == company.id
        ).order_by(PlacementDrive.created_at.desc()).all()
        return [d.to_dict() for d in drives]

    @classmethod
    def create_drive(cls, user_id, payload):
        company = cls.get_company_by_user(user_id)
        
        if company.approval_status != 'approved':
            raise Forbidden('Your company must be approved by admin before creating drives')

        if not payload or not payload.get('job_role'):
            raise ValidationError('job_role is required')

        deadline_val = None
        if payload.get('deadline'):
            try:
                deadline_val = date.fromisoformat(payload['deadline'])
            except ValueError:
                raise ValidationError('Deadline date format should be YYYY-MM-DD')

        drive = PlacementDrive(
            company_id=company.id,
            title=payload.get('title', payload['job_role']),
            job_role=payload['job_role'],
            package=payload.get('package'),
            eligibility=payload.get('eligibility'),
            openings=payload.get('openings', 1),
            deadline=deadline_val,
            description=payload.get('description'),
            status='pending'
        )

        db.session.add(drive)
        db.session.commit()
        return drive.to_dict()

    @classmethod
    def get_drive(cls, user_id, drive_id):
        company = cls.get_company_by_user(user_id)
        drive = db.session.query(PlacementDrive).filter(
            PlacementDrive.id == drive_id,
            PlacementDrive.company_id == company.id
        ).first()
        
        if not drive:
            raise NotFound('Placement drive not found')
        return drive.to_dict()

    @classmethod
    def update_drive(cls, user_id, drive_id, payload):
        company = cls.get_company_by_user(user_id)
        drive = db.session.query(PlacementDrive).filter(
            PlacementDrive.id == drive_id,
            PlacementDrive.company_id == company.id
        ).first()
        
        if not drive:
            raise NotFound('Placement drive not found')
            
        updatable = ['title', 'job_role', 'package', 'eligibility', 'openings', 'description']
        for field in updatable:
            if field in payload:
                setattr(drive, field, payload[field])

        if 'deadline' in payload and payload['deadline']:
            try:
                drive.deadline = date.fromisoformat(payload['deadline'])
            except ValueError:
                raise ValidationError('Deadline format should be YYYY-MM-DD')

        if 'status' in payload and payload['status'] in ('pending', 'open', 'closed'):
            drive.status = payload['status']

        db.session.commit()
        return drive.to_dict()

    @classmethod
    def delete_drive(cls, user_id, drive_id):
        company = cls.get_company_by_user(user_id)
        drive = db.session.query(PlacementDrive).filter(
            PlacementDrive.id == drive_id,
            PlacementDrive.company_id == company.id
        ).first()
        
        if not drive:
            raise NotFound('Placement drive not found')
            
        db.session.delete(drive)
        db.session.commit()

    @classmethod
    def close_drive(cls, user_id, drive_id):
        company = cls.get_company_by_user(user_id)
        drive = db.session.query(PlacementDrive).filter(
            PlacementDrive.id == drive_id,
            PlacementDrive.company_id == company.id
        ).first()
        
        if not drive:
            raise NotFound('Placement drive not found')
            
        drive.status = 'closed'
        db.session.commit()
        return drive.to_dict()

    @classmethod
    def get_received_applications(cls, user_id, status_filter, drive_filter):
        company = cls.get_company_by_user(user_id)
        drive_ids = company.drive_ids

        query = db.session.query(Application).filter(Application.drive_id.in_(drive_ids))

        if status_filter:
            query = query.filter(Application.application_status == status_filter.lower())

        if drive_filter:
            query = query.filter(Application.drive_id == int(drive_filter))

        apps = query.order_by(Application.applied_at.desc()).all()
        return [a.to_dict() for a in apps]

    @classmethod
    def verify_app_owner(cls, company, app_record):
        if app_record.drive_id not in company.drive_ids:
            raise Forbidden('This application does not belong to your drives')

    @classmethod
    def _notify_student_status_update(cls, app, status, extra_info=None):
        """Sends automated HTML email and GChat notification to the applicant when status updates."""
        try:
            from services.email_service import send_email
            from services.gchat_service import send_gchat_notification

            student = app.student
            if not student or not student.user:
                return

            recipient_email = student.user.email
            student_name = student.user.name
            drive_title = app.drive.title if app.drive else 'Placement Drive'
            company_name = app.drive.company.company_name if app.drive and app.drive.company else 'Company'

            subject = f"Application Status Update: {status.capitalize()} - {company_name}"
            status_display = status.capitalize()
            details_html = f"<p style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'><strong>Details:</strong> {extra_info}</p>" if extra_info else ""

            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
              <h2 style="color: #0d6efd; margin-top: 0;">Application Status Update</h2>
              <p>Dear <strong>{student_name}</strong>,</p>
              <p>Your application status for <strong>{drive_title}</strong> at <strong>{company_name}</strong> has been updated to:</p>
              <div style="font-size: 20px; font-weight: bold; margin: 16px 0; padding: 12px; background-color: #eef2ff; color: #0d6efd; border-radius: 6px; text-align: center;">
                {status_display}
              </div>
              {details_html}
              <p>Please log in to your student placement dashboard for further information.</p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
              <p style="font-size: 12px; color: #888;">Automated notification from University Placement Portal</p>
            </div>
            """

            send_email(recipient_email, subject, html_body)
            send_gchat_notification(f"Application Update: {student_name} -> {status_display} ({drive_title} at {company_name})")
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Could not dispatch notification to student: {exc}")

    @classmethod
    def shortlist_student(cls, user_id, app_id):
        company = cls.get_company_by_user(user_id)
        app = db.session.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise NotFound('Application not found')

        cls.verify_app_owner(company, app)
        app.application_status = 'shortlisted'

        student = app.student
        if student and student.placement_status not in ('Placed', 'Interview'):
            student.placement_status = 'Applied'

        db.session.commit()
        cls._notify_student_status_update(app, 'shortlisted')
        return app.to_dict()

    @classmethod
    def reject_application(cls, user_id, app_id):
        company = cls.get_company_by_user(user_id)
        app = db.session.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise NotFound('Application not found')

        cls.verify_app_owner(company, app)
        app.application_status = 'rejected'
        db.session.commit()
        cls._notify_student_status_update(app, 'rejected')
        return app.to_dict()

    @classmethod
    def update_application_status(cls, user_id, app_id, new_status):
        allowed = ['shortlisted', 'selected', 'rejected', 'interview', 'applied']
        clean_status = (new_status or '').lower().strip()
        if clean_status not in allowed:
            raise ValidationError(f"Status must be one of: {', '.join(allowed)}")

        company = cls.get_company_by_user(user_id)
        app = db.session.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise NotFound('Application not found')

        cls.verify_app_owner(company, app)
        app.application_status = clean_status

        if app.student:
            if clean_status == 'selected':
                app.student.placement_status = 'Placed'
            elif clean_status == 'interview':
                app.student.placement_status = 'Interview'
            elif clean_status == 'shortlisted':
                if app.student.placement_status not in ('Placed', 'Interview'):
                    app.student.placement_status = 'Applied'

        db.session.commit()
        cls._notify_student_status_update(app, clean_status)
        return app.to_dict()

    @classmethod
    def get_scheduled_interviews(cls, user_id):
        company = cls.get_company_by_user(user_id)
        drive_ids = company.drive_ids

        apps = db.session.query(Application).filter(
            Application.drive_id.in_(drive_ids)
        ).all()

        return [
            {
                **app.interview.to_dict(),
                'student_name': app.student.user.name if app.student and app.student.user else '',
                'drive_title': app.drive.title if app.drive else ''
            }
            for app in apps if app.interview
        ]

    @classmethod
    def schedule_interview(cls, user_id, payload):
        company = cls.get_company_by_user(user_id)
        
        app_id = payload.get('application_id')
        if not app_id:
            raise ValidationError('application_id is required')

        app = db.session.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise NotFound('Application not found')

        cls.verify_app_owner(company, app)

        # Enforce Rule: Interview scheduling only allowed for shortlisted applicants
        if app.application_status not in ('shortlisted', 'interview'):
            raise ValidationError('Interviews can only be scheduled for shortlisted applicants. Please shortlist candidate first.')

        interview = app.interview if app.interview else Interview(application_id=app_id)
        if not app.interview:
            db.session.add(interview)

        if payload.get('interview_date'):
            try:
                interview.interview_date = date.fromisoformat(payload['interview_date'])
            except ValueError:
                raise ValidationError('Interview date format should be YYYY-MM-DD')

        interview.interview_time = payload.get('interview_time')
        interview.interview_mode = payload.get('interview_mode', 'online')
        interview.interview_link = payload.get('interview_link')
        interview.round_name = payload.get('round_name')
        interview.remarks = payload.get('remarks')

        app.application_status = 'interview'
        if app.student:
            app.student.placement_status = 'Interview'

        db.session.commit()
        extra_note = f"Round: {payload.get('round_name', 'Interview')} | Date: {payload.get('interview_date')} {payload.get('interview_time', '')} ({payload.get('interview_mode', 'online')})"
        cls._notify_student_status_update(app, 'interview', extra_info=extra_note)
        return interview.to_dict()

    @classmethod
    def send_interview_email(cls, user_id, interview_id):
        company = cls.get_company_by_user(user_id)
        
        interview = db.session.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise NotFound('Interview not found')

        app = interview.application
        if not app:
            raise NotFound('Associated application not found')

        cls.verify_app_owner(company, app)

        student = app.student
        if not student or not student.user:
            raise ValidationError('Candidate has no registered email address')

        from services.email_service import send_email

        recipient_email = student.user.email
        student_name = student.user.name
        drive_title = app.drive.title if app.drive else 'Placement Drive'
        company_name = app.drive.company.company_name if app.drive and app.drive.company else 'Company'
        
        round_name = interview.round_name or 'Interview'
        date_str = interview.interview_date.strftime('%b %d, %Y') if interview.interview_date else 'TBD'
        time_str = interview.interview_time or 'TBD'
        mode_str = (interview.interview_mode or 'online').capitalize()
        link_str = f'<a href="{interview.interview_link}">{interview.interview_link}</a>' if interview.interview_link else 'N/A'

        subject = f"Interview Reminder: {round_name} - {company_name}"

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #0d6efd; margin-top: 0;">Interview Reminder</h2>
            <p>Dear <strong>{student_name}</strong>,</p>
            <p>This is a reminder for your upcoming interview for the <strong>{drive_title}</strong> role at <strong>{company_name}</strong>.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Round:</strong> {round_name}</p>
                <p style="margin: 5px 0;"><strong>Date:</strong> {date_str}</p>
                <p style="margin: 5px 0;"><strong>Time:</strong> {time_str}</p>
                <p style="margin: 5px 0;"><strong>Mode:</strong> {mode_str}</p>
                <p style="margin: 5px 0;"><strong>Link / Location:</strong> {link_str}</p>
            </div>
            
            <p>Please ensure you are prepared and join on time. Best of luck!</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
            <p style="font-size: 12px; color: #888;">Automated notification from University Placement Portal</p>
        </div>
        """

        success = send_email(recipient_email, subject, html_body)
        if not success:
            raise ValidationError('Failed to send email. Please try again later.')

        return True


    @classmethod
    def get_result_candidates(cls, user_id):
        company = cls.get_company_by_user(user_id)
        drive_ids = company.drive_ids

        apps = db.session.query(Application).filter(
            Application.drive_id.in_(drive_ids),
            Application.application_status.in_(['interview', 'shortlisted'])
        ).all()

        return [
            {
                'application_id': app.id,
                'student_name': app.student.user.name if app.student and app.student.user else '',
                'drive_title': app.drive.title if app.drive else '',
                'drive_role': app.drive.job_role if app.drive else '',
                'application_status': app.application_status,
                'result': app.result.to_dict() if app.result else None
            }
            for app in apps
        ]

    @classmethod
    def publish_result(cls, user_id, payload):
        company = cls.get_company_by_user(user_id)
        
        app_id = payload.get('application_id')
        status_res = payload.get('result_status')

        if not app_id:
            raise ValidationError('application_id is required')

        if status_res not in ('selected', 'rejected'):
            raise ValidationError('result_status must be selected or rejected')

        app = db.session.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise NotFound('Application not found')

        cls.verify_app_owner(company, app)

        if app.result:
            app.result.result_status = status_res
            app.result.remarks = payload.get('remarks')
        else:
            new_res = Result(
                application_id=app_id,
                result_status=status_res,
                remarks=payload.get('remarks')
            )
            db.session.add(new_res)

        app.application_status = status_res

        if status_res == 'selected' and app.student:
            app.student.placement_status = 'Placed'

        db.session.commit()
        cls._notify_student_status_update(app, status_res, extra_info=payload.get('remarks'))
