from datetime import datetime, timezone
from models import db, DictMixin

class ReminderHistory(db.Model, DictMixin):
    """
    Tracks which students have already received a deadline reminder
    for a specific placement drive. This ensures idempotency and
    prevents duplicate emails if the Celery task runs multiple times.
    """
    __tablename__ = 'reminder_history'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship('Student', backref=db.backref('reminders', cascade='all, delete-orphan'))
    drive = db.relationship('PlacementDrive', backref=db.backref('reminders', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='one_reminder_per_student_drive'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'drive_id': self.drive_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
