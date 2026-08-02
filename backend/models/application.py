from datetime import datetime, timezone
from models import db, DictMixin

STAGE_MAP = {
    'applied': 'Screening',
    'shortlisted': 'HR Round',
    'interview': 'Technical',
    'selected': 'Selected',
    'rejected': 'Rejected'
}

PROGRESS_MAP = {
    'applied': 20,
    'shortlisted': 45,
    'interview': 70,
    'selected': 100,
    'rejected': 0
}

class Application(db.Model, DictMixin):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    application_status = db.Column(db.String(30), default='applied')
    cover_note = db.Column(db.Text)
    resume_path = db.Column(db.String(256))
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship('Student', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates='applications')
    interview = db.relationship('Interview', back_populates='application', uselist=False, cascade='all, delete-orphan')
    result = db.relationship('Result', back_populates='application', uselist=False, cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='one_application_per_drive'),
    )

    def to_dict(self, include_student=True, include_drive=True):
        fields = ['id', 'student_id', 'drive_id', 'application_status', 'cover_note']
        dict_out = self.as_dict(fields)
        dict_out['applied_at'] = self.applied_at.strftime('%Y-%m-%d %H:%M') if self.applied_at else None
        dict_out['stage'] = STAGE_MAP.get(self.application_status, 'Screening')
        dict_out['progress'] = PROGRESS_MAP.get(self.application_status, 20)

        linked_student = self.student
        effective_resume = self.resume_path or (linked_student.resume_path if linked_student else None)
        dict_out['resume_path'] = effective_resume
        # Build an absolute backend URL so the admin can open the resume directly.
        # Using the admin-scoped endpoint avoids routing through the Vue app,
        # which would otherwise redirect to /auth/login for unrecognised paths.
        dict_out['resume_url'] = (
            f"http://localhost:5000/api/admin/resumes/{effective_resume}"
            if effective_resume else None
        )

        if include_student and linked_student:
            linked_user = linked_student.user
            dict_out['student_name'] = linked_user.name if linked_user else ''
            dict_out['student_register_number'] = linked_student.register_number
            dict_out['student_department'] = linked_student.department
            dict_out['student_cgpa'] = linked_student.cgpa
            dict_out['student_resume_path'] = effective_resume
            dict_out['student_resume_url'] = dict_out['resume_url']

        linked_drive = self.drive
        if include_drive and linked_drive:
            dict_out['drive_title'] = linked_drive.title
            dict_out['drive_role'] = linked_drive.job_role
            dict_out['drive_package'] = linked_drive.package
            
            linked_company = linked_drive.company
            dict_out['company_name'] = linked_company.company_name if linked_company else ''

        if self.interview:
            dict_out['interview'] = self.interview.to_dict()

        if self.result:
            dict_out['result'] = self.result.to_dict()

        return dict_out
