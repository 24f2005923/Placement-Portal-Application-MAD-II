from datetime import datetime, timezone
from models import db, DictMixin


class InterviewReminderHistory(db.Model, DictMixin):
    """
    Tracks which students have already received an interview reminder
    for a specific interview. This ensures idempotency and prevents
    duplicate emails / SMS / GChat messages when the Celery task
    fires more than once on the same day.

    Unique constraint: one record per (student_id, interview_id) pair.
    """
    __tablename__ = 'interview_reminder_history'

    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.id'),   nullable=False)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    sent_at     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student   = db.relationship('Student',   backref=db.backref('interview_reminders', cascade='all, delete-orphan'))
    interview = db.relationship('Interview', backref=db.backref('reminder_histories',  cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'interview_id', name='uq_interview_reminder_per_student'),
    )

    def to_dict(self):
        return {
            'id':           self.id,
            'student_id':   self.student_id,
            'interview_id': self.interview_id,
            'sent_at':      self.sent_at.isoformat() if self.sent_at else None,
        }
