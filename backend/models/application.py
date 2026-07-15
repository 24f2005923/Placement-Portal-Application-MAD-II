from datetime import datetime
from models import db


# Application table - when a student applies for a placement drive, it creates a row here
class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    application_status = db.Column(db.String(30), default='applied')
    # application_status values: applied / shortlisted / interview / selected / rejected
    cover_note = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='applications')
    drive = db.relationship('PlacementDrive', back_populates='applications')
    interview = db.relationship('Interview', back_populates='application', uselist=False, cascade='all, delete-orphan')
    result = db.relationship('Result', back_populates='application', uselist=False, cascade='all, delete-orphan')

    # prevent student from applying twice to the same drive
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='one_application_per_drive'),
    )

    def to_dict(self, include_student=True, include_drive=True):
        # map status to a readable stage name for the frontend
        stage_names = {
            'applied': 'Screening',
            'shortlisted': 'HR Round',
            'interview': 'Technical',
            'selected': 'Selected',
            'rejected': 'Rejected'
        }
        # map status to progress percentage for progress bar
        progress_values = {
            'applied': 20,
            'shortlisted': 45,
            'interview': 70,
            'selected': 100,
            'rejected': 0
        }

        app_data = {
            'id': self.id,
            'student_id': self.student_id,
            'drive_id': self.drive_id,
            'application_status': self.application_status,
            'cover_note': self.cover_note,
            'applied_at': self.applied_at.strftime('%Y-%m-%d %H:%M') if self.applied_at else None,
            'stage': stage_names.get(self.application_status, 'Screening'),
            'progress': progress_values.get(self.application_status, 20)
        }

        if include_student and self.student:
            app_data['student_name'] = self.student.user.name if self.student.user else ''
            app_data['student_register_number'] = self.student.register_number
            app_data['student_department'] = self.student.department
            app_data['student_cgpa'] = self.student.cgpa

        if include_drive and self.drive:
            app_data['drive_title'] = self.drive.title
            app_data['drive_role'] = self.drive.job_role
            app_data['drive_package'] = self.drive.package
            app_data['company_name'] = self.drive.company.company_name if self.drive.company else ''

        if self.interview:
            app_data['interview'] = self.interview.to_dict()

        if self.result:
            app_data['result'] = self.result.to_dict()

        return app_data
