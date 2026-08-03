from models import db
from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.user import User
from exceptions import NotFound, ValidationError
from utils.pagination import paginate_query
from utils.stats import create_stat_item
from utils.repository import BaseRepository
from utils.validators import validate_status_choice

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
        total_applications = db.session.query(Application).count()

        return [
            create_stat_item('Total Students', student_total, 'bi-people', 'primary'),
            create_stat_item('Total Companies', active_company, 'bi-buildings', 'success'),
            create_stat_item('Active Drives', open_drives, 'bi-megaphone', 'warning'),
            create_stat_item('Total Applications', total_applications, 'bi-file-earmark-text', 'danger')
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
    def get_settings():
        return portal_settings.get_all()

    @staticmethod
    def update_settings(payload):
        return portal_settings.update(payload)

    @staticmethod
    def get_students(search_term='', status_filter='', page_num=1, records_per_page=20):
        query = db.session.query(Student).join(User)

        clean_search = str(search_term or '').strip()
        if clean_search:
            wildcard = f"%{clean_search}%"
            query = query.filter(
                db.or_(
                    User.name.ilike(wildcard),
                    User.email.ilike(wildcard),
                    Student.register_number.ilike(wildcard),
                    Student.department.ilike(wildcard),
                    Student.phone.ilike(wildcard),
                    Student.preferred_role.ilike(wildcard)
                )
            )

        clean_status = str(status_filter or '').strip().lower()
        if clean_status and clean_status != 'all':
            if clean_status == 'inactive':
                query = query.filter(User.status == 'inactive')
            elif clean_status == 'active':
                query = query.filter(User.status == 'active')
            else:
                query = query.filter(Student.placement_status.ilike(clean_status))

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['students'] = [s.to_dict() for s in paginated.pop('items')]
        return paginated

    @staticmethod
    def get_student_detail(student_id):
        student = BaseRepository.get_by_id_or_404(Student, student_id, 'Student not found')
        
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
        student = BaseRepository.get_by_id_or_404(Student, student_id, 'Student not found')

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
        validate_status_choice(new_status, ['active', 'inactive'])
        student = BaseRepository.get_by_id_or_404(Student, student_id, 'Student not found')

        student.user.status = new_status
        db.session.commit()

    @staticmethod
    def get_companies(search_term='', status_filter='', page_num=1, records_per_page=20):
        query = db.session.query(Company).join(User)

        clean_search = str(search_term or '').strip()
        if clean_search:
            wildcard = f"%{clean_search}%"
            query = query.filter(
                db.or_(
                    Company.company_name.ilike(wildcard),
                    User.name.ilike(wildcard),
                    User.email.ilike(wildcard),
                    Company.contact_email.ilike(wildcard),
                    Company.contact_person.ilike(wildcard),
                    Company.contact_phone.ilike(wildcard),
                    Company.industry.ilike(wildcard),
                    Company.city.ilike(wildcard)
                )
            )

        clean_status = str(status_filter or '').strip().lower()
        if clean_status and clean_status != 'all':
            if clean_status == 'blacklisted':
                query = query.filter(Company.blacklisted == True)
            else:
                query = query.filter(
                    Company.approval_status == clean_status,
                    Company.blacklisted == False
                )

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['companies'] = [c.to_dict() for c in paginated.pop('items')]
        return paginated

    @staticmethod
    def get_company_detail(company_id):
        company = BaseRepository.get_by_id_or_404(Company, company_id, 'Company not found')
        return company.to_dict(show_drives=True)

    @staticmethod
    def update_company_approval(company_id, status_val):
        company = BaseRepository.get_by_id_or_404(Company, company_id, 'Company not found')
        company.approval_status = status_val
        if status_val == 'approved':
            company.blacklisted = False
        db.session.commit()

    @staticmethod
    def blacklist_company(company_id, blacklisted_bool):
        company = BaseRepository.get_by_id_or_404(Company, company_id, 'Company not found')
        company.blacklisted = blacklisted_bool
        db.session.commit()

    @staticmethod
    def get_drives(search_term='', status_filter='', page_num=1, records_per_page=20):
        query = db.session.query(PlacementDrive).join(Company)

        clean_search = str(search_term or '').strip()
        if clean_search:
            wildcard = f"%{clean_search}%"
            query = query.filter(
                db.or_(
                    PlacementDrive.title.ilike(wildcard),
                    PlacementDrive.job_role.ilike(wildcard),
                    Company.company_name.ilike(wildcard)
                )
            )

        clean_status = str(status_filter or '').strip().lower()
        if clean_status and clean_status != 'all':
            query = query.filter(PlacementDrive.status == clean_status)

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['drives'] = [d.to_dict() for d in paginated.pop('items')]
        return paginated

    @staticmethod
    def get_drive_detail(drive_id):
        drive = BaseRepository.get_by_id_or_404(PlacementDrive, drive_id, 'Drive not found')
        return drive.to_dict()

    @staticmethod
    def update_drive_status(drive_id, status_val):
        validate_status_choice(status_val, ['pending', 'open', 'closed', 'rejected'])
        drive = BaseRepository.get_by_id_or_404(PlacementDrive, drive_id, 'Drive not found')
            
        drive.status = status_val
        db.session.commit()

    @staticmethod
    def get_applications(search_term='', status_filter='', page_num=1, records_per_page=20):
        query = db.session.query(Application).join(Student).join(User).join(PlacementDrive).join(Company)

        if search_term:
            wildcard = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    User.name.ilike(wildcard),
                    Student.register_number.ilike(wildcard),
                    PlacementDrive.title.ilike(wildcard),
                    PlacementDrive.job_role.ilike(wildcard),
                    Company.company_name.ilike(wildcard)
                )
            )

        if status_filter and status_filter.lower() != 'all':
            query = query.filter(Application.application_status == status_filter.lower())

        query = query.order_by(Application.applied_at.desc())

        paginated = paginate_query(query, page_num, records_per_page)
        paginated['applications'] = [a.to_dict() for a in paginated.pop('items')]
        return paginated

    @staticmethod
    def update_application_status(application_id, status_val):
        clean_status = validate_status_choice(status_val, ['applied', 'shortlisted', 'interview', 'selected', 'rejected'])

        app = BaseRepository.get_by_id_or_404(Application, application_id, 'Application not found')

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
        return app.to_dict()

    @staticmethod
    def get_report_analytics():
        """
        Compute live placement analytics from the database using efficient
        aggregate queries.  All values are derived from actual records —
        no hardcoded fallbacks, no mock data.  Returns zeros / empty lists
        when the database contains no matching rows.
        """
        from sqlalchemy import func

        # ── Student metrics ────────────────────────────────────────────
        total_students = db.session.query(func.count(Student.id)).scalar() or 0
        placed_count   = db.session.query(func.count(Student.id)).filter(
            Student.placement_status == 'Placed'
        ).scalar() or 0
        placement_rate = round((placed_count / total_students) * 100, 1) if total_students else 0.0

        # ── Drive metrics ──────────────────────────────────────────────
        total_drives  = db.session.query(func.count(PlacementDrive.id)).scalar() or 0
        open_drives   = db.session.query(func.count(PlacementDrive.id)).filter(
            PlacementDrive.status == 'open'
        ).scalar() or 0
        closed_drives = db.session.query(func.count(PlacementDrive.id)).filter(
            PlacementDrive.status == 'closed'
        ).scalar() or 0

        # ── Application funnel metrics ─────────────────────────────────
        total_apps = db.session.query(func.count(Application.id)).scalar() or 0

        shortlisted = db.session.query(func.count(Application.id)).filter(
            Application.application_status.in_(['shortlisted', 'interview', 'selected'])
        ).scalar() or 0

        in_interview = db.session.query(func.count(Application.id)).filter(
            Application.application_status == 'interview'
        ).scalar() or 0

        selected = db.session.query(func.count(Application.id)).filter(
            Application.application_status == 'selected'
        ).scalar() or 0

        rejected = db.session.query(func.count(Application.id)).filter(
            Application.application_status == 'rejected'
        ).scalar() or 0

        shortlist_rate  = round((shortlisted / total_apps) * 100, 1) if total_apps else 0.0
        selection_rate  = round((selected    / total_apps) * 100, 1) if total_apps else 0.0
        interview_rate  = round((in_interview / total_apps) * 100, 1) if total_apps else 0.0

        # ── Department-wise placement breakdown ────────────────────────
        dept_rows = (
            db.session.query(Student.department, func.count(Student.id).label('count'))
            .filter(Student.department.isnot(None), Student.department != '')
            .group_by(Student.department)
            .order_by(func.count(Student.id).desc())
            .all()
        )
        dept_placed_rows = (
            db.session.query(Student.department, func.count(Student.id).label('placed'))
            .filter(Student.placement_status == 'Placed',
                    Student.department.isnot(None),
                    Student.department != '')
            .group_by(Student.department)
            .all()
        )
        placed_by_dept = {row.department: row.placed for row in dept_placed_rows}

        dept_breakdown = [
            {
                'department': row.department,
                'total': row.count,
                'placed': placed_by_dept.get(row.department, 0),
                'rate': round((placed_by_dept.get(row.department, 0) / row.count) * 100, 1)
                        if row.count else 0.0
            }
            for row in dept_rows
        ]

        return {
            'students': {
                'total': total_students,
                'placed': placed_count,
                'placement_rate': placement_rate,
            },
            'drives': {
                'total': total_drives,
                'open': open_drives,
                'closed': closed_drives,
            },
            'applications': {
                'total': total_apps,
                'shortlisted': shortlisted,
                'in_interview': in_interview,
                'selected': selected,
                'rejected': rejected,
                'shortlist_rate': shortlist_rate,
                'selection_rate': selection_rate,
                'interview_rate': interview_rate,
            },
            'department_breakdown': dept_breakdown,
        }

    @staticmethod
    def get_top_companies(limit=10):
        """
        Return companies ranked by total selected (placed) students.
        Uses a single joined query — avoids per-company sub-loops.
        Companies with zero selections are included only when limit allows.
        """
        from sqlalchemy import func

        # Single query: join Company → PlacementDrive → Application
        rows = (
            db.session.query(
                Company.id,
                Company.company_name,
                Company.industry,
                func.count(PlacementDrive.id).label('drive_count'),
                func.sum(
                    db.case(
                        (Application.application_status == 'selected', 1),
                        else_=0
                    )
                ).label('selections'),
                func.count(Application.id).label('total_apps'),
            )
            .outerjoin(PlacementDrive, PlacementDrive.company_id == Company.id)
            .outerjoin(Application, Application.drive_id == PlacementDrive.id)
            .filter(Company.approval_status == 'approved', Company.blacklisted == False)
            .group_by(Company.id, Company.company_name, Company.industry)
            .order_by(db.text('selections DESC'))
            .limit(limit)
            .all()
        )

        return [
            {
                'company_name': row.company_name,
                'industry': row.industry or '—',
                'drives': row.drive_count or 0,
                'total_applications': row.total_apps or 0,
                'selections': row.selections or 0,
            }
            for row in rows
        ]
