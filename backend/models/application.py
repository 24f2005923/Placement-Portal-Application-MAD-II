from datetime import datetime, timezone
from models import db

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    application_status = db.Column(db.String(30), default='applied') # applied, shortlisted, interview, selected, rejected
    cover_note = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship('Student', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates='applications')
    interview = db.relationship('Interview', back_populates='application', uselist=False, cascade='all, delete-orphan')
    result = db.relationship('Result', back_populates='application', uselist=False, cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='one_application_per_drive'),
    )

    def to_dict(self, include_student=True, include_drive=True):
        # Progress maps
        stages = {
            'applied': 'Screening',
            'shortlisted': 'HR Round',
            'interview': 'Technical',
            'selected': 'Selected',
            'rejected': 'Rejected'
        }
        progress_levels = {
            'applied': 20,
            'shortlisted': 45,
            'interview': 70,
            'selected': 100,
            'rejected': 0
        }

        dict_out = {}
        dict_out['id'] = self.id
        dict_out['student_id'] = self.student_id
        dict_out['drive_id'] = self.drive_id
        dict_out['application_status'] = self.application_status
        dict_out['cover_note'] = self.cover_note
        dict_out['applied_at'] = self.applied_at.strftime('%Y-%m-%d %H:%M') if self.applied_at else None
        dict_out['stage'] = stages.get(self.application_status, 'Screening')
        dict_out['progress'] = progress_levels.get(self.application_status, 20)

        # Merge student properties
        linked_student = self.student
        if include_student and linked_student:
            dict_out['student_name'] = linked_student.user.name if linked_student.user else ''
            dict_out['student_register_number'] = linked_student.register_number
            dict_out['student_department'] = linked_student.department
            dict_out['student_cgpa'] = linked_student.cgpa

        # Merge drive properties
        linked_drive = self.drive
        if include_drive and linked_drive:
            dict_out['drive_title'] = linked_drive.title
            dict_out['drive_role'] = linked_drive.job_role
            dict_out['drive_package'] = linked_drive.package
            dict_out['company_name'] = linked_drive.company.company_name if linked_drive.company else ''

        if self.interview:
            dict_out['interview'] = self.interview.to_dict()

        if self.result:
            dict_out['result'] = self.result.to_dict()

        return dict_out

