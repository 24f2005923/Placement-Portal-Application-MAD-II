from models import db
from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.user import User
from exceptions import NotFound, ValidationError
from utils.pagination import paginate_query
from utils.stats import create_stat_item

class PortalSettings:
    """Manages system settings for the placement portal."""
    def __init__(self):
        self._settings = {
            'portal_name': 'University Placement Portal',
            'academic_year': '2025-26',
            'notification_email': 'admin@admin.com',
            'self_registration': True,
            'company_approvals': True,
            'instant_notifications': False
        }
    
    def get_all(self):
        return self._settings.copy()
        
    def update(self, new_data):
        if new_data:
            self._settings.update(new_data)
        return self.get_all()

portal_settings = PortalSettings()

class AdminService:
    """Service layer handling administrative workflows."""
    
    @staticmethod
    def get_dashboard_stats():
        student_total = db.session.query(Student).count()
        active_company = db.session.query(Company).filter(Company.blacklisted == False).count()
        open_drives = db.session.query(PlacementDrive).filter(
            PlacementDrive.status.in_(['open', 'approved'])
        ).count()
        placed_students = db.session.query(Student).filter(Student.placement_status == 'Placed').count()

        return [
            create_stat_item('Total Students', student_total, 'bi-people', 'primary'),
            create_stat_item('Total Companies', active_company, 'bi-buildings', 'success'),
            create_stat_item('Active Drives', open_drives, 'bi-megaphone', 'warning'),
            create_stat_item('Placed Students', placed_students, 'bi-award', 'danger')
        ]

    @staticmethod
    def get_recent_activities():
        activities = []
        latest_apps = db.session.query(Application).order_by(Application.applied_at.desc()).limit(3).all()
        
        activities.extend([
            {
                'title': f"{app.student.user.name if app.student and app.student.user else ''} applied for {app.drive.title if app.drive else 'Unknown'}",
                'meta': app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else '',
                'tone': 'primary'
            }
            for app in latest_apps
        ])

        pending_companies = db.session.query(Company).filter(Company.approval_status == 'pending').count()
        if pending_companies > 0:
            activities.append({
                'title': f"{pending_companies} company registration(s) need approval",
                'meta': 'Pending',
                'tone': 'danger'
            })

        pending_drives = db.session.query(PlacementDrive).filter(PlacementDrive.status == 'pending').count()
        if pending_drives > 0:
            activities.append({
                'title': f"{pending_drives} placement drive(s) waiting for approval",
                'meta': 'Pending',
                'tone': 'warning'
            })

        return activities

    @staticmethod
    def get_report_stats():
        student_total = db.session.query(Student).count()
        placed_students = db.session.query(Student).filter(Student.placement_status == 'Placed').count()
        placement_rate = round((placed_students / student_total) * 100, 1) if student_total > 0 else 0.0

        drives_total = db.session.query(PlacementDrive).count()
        approved_drives = db.session.query(PlacementDrive).filter(
            PlacementDrive.status.in_(['open', 'approved', 'closed'])
        ).count()
        drive_conversion = round((approved_drives / drives_total) * 100, 1) if drives_total > 0 else 0.0

        total_apps = db.session.query(Application).count()
        selected_apps = db.session.query(Application).filter(Application.application_status == 'selected').count()
        interview_success = round((selected_apps / total_apps) * 100, 1) if total_apps > 0 else 0.0

        return [
            create_stat_item('Placement Rate', f"{placement_rate}%", 'bi-graph-up', 'primary'),
            create_stat_item('Drive Conversion', f"{drive_conversion}%", 'bi-arrow-repeat', 'success'),
            create_stat_item('Average Package', 'N/A', 'bi-currency-rupee', 'warning'),
            create_stat_item('Interview Success', f"{interview_success}%", 'bi-person-check', 'danger')
        ]

    @staticmethod
    def get_settings():
        return portal_settings.get_all()

    @staticmethod
    def update_settings(payload):
        return portal_settings.update(payload)

    @staticmethod
    def get_students(search_term, status_filter, page_num, records_per_page=20):
        query = db.session.query(Student).join(User)

        if search_term:
            wildcard = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    User.name.ilike(wildcard),
                    Student.register_number.ilike(wildcard),
                    Student.department.ilike(wildcard)
                )
            )

        if status_filter and status_filter.lower() != 'all':
            if status_filter.lower() == 'inactive':
                query = query.filter(User.status == 'inactive')
            else:
                query = query.filter(Student.placement_status.ilike(status_filter))

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['students'] = [s.to_dict() for s in paginated.pop('items')]
        return paginated

    @staticmethod
    def get_student_detail(student_id):
        student = db.session.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise NotFound('Student not found')
            
        student_dict = student.to_dict()
        student_dict['placement_history'] = [
            {
                'company': app.drive.company.company_name if app.drive and app.drive.company else '',
                'role': app.drive.job_role if app.drive else '',
                'year': app.applied_at.year if app.applied_at else '',
                'package': app.drive.package if app.drive else ''
            }
            for app in student.applications if app.result and app.result.result_status == 'selected'
        ]
        return student_dict

    @staticmethod
    def update_student(student_id, payload):
        student = db.session.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise NotFound('Student not found')

        if 'name' in payload:
            student.user.name = payload['name']
        if 'email' in payload:
            student.user.email = payload['email'].lower().strip()

        updatable_fields = ['department', 'year', 'cgpa', 'phone', 'address',
                            'marks_10th', 'marks_12th', 'backlogs', 'graduation_year', 'preferred_role']
                            
        for field in updatable_fields:
            if field in payload:
                setattr(student, field, payload[field])

        if 'skills' in payload:
            student.save_skills(payload['skills'])

        db.session.commit()
        return student.to_dict()

    @staticmethod
    def change_student_status(student_id, new_status):
        if new_status not in ('active', 'inactive'):
            raise ValidationError('Status must be active or inactive')
            
        student = db.session.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise NotFound('Student not found')

        student.user.status = new_status
        db.session.commit()

    @staticmethod
    def get_companies(search_term, status_filter, page_num, records_per_page=20):
        query = db.session.query(Company).join(User)

        if search_term:
            wildcard = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    Company.company_name.ilike(wildcard),
                    Company.industry.ilike(wildcard),
                    Company.city.ilike(wildcard)
                )
            )

        if status_filter and status_filter.lower() != 'all':
            if status_filter.lower() == 'blacklisted':
                query = query.filter(Company.blacklisted == True)
            else:
                query = query.filter(
                    Company.approval_status == status_filter.lower(),
                    Company.blacklisted == False
                )

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['companies'] = [c.to_dict() for c in paginated.pop('items')]
        return paginated

    @staticmethod
    def get_company_detail(company_id):
        company = db.session.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFound('Company not found')
        return company.to_dict(show_drives=True)

    @staticmethod
    def update_company_approval(company_id, status_val):
        company = db.session.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFound('Company not found')
        company.approval_status = status_val
        if status_val == 'approved':
            company.blacklisted = False
        db.session.commit()

    @staticmethod
    def blacklist_company(company_id, blacklisted_bool):
        company = db.session.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise NotFound('Company not found')
        company.blacklisted = blacklisted_bool
        db.session.commit()

    @staticmethod
    def get_drives(status_filter, page_num, records_per_page=20):
        query = db.session.query(PlacementDrive).join(Company)

        if status_filter and status_filter.lower() != 'all':
            query = query.filter(PlacementDrive.status == status_filter.lower())

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['drives'] = [d.to_dict() for d in paginated.pop('items')]
        return paginated

    @staticmethod
    def get_drive_detail(drive_id):
        drive = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
        if not drive:
            raise NotFound('Drive not found')
        return drive.to_dict()

    @staticmethod
    def update_drive_status(drive_id, status_val):
        allowed = ['pending', 'open', 'closed', 'rejected']
        if status_val not in allowed:
            raise ValidationError(f"Status must be one of: {', '.join(allowed)}")
            
        drive = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
        if not drive:
            raise NotFound('Drive not found')
            
        drive.status = status_val
        db.session.commit()
