from models import db


# Interview table - stores interview schedule details for shortlisted students
class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    interview_date = db.Column(db.Date)
    interview_time = db.Column(db.String(10))
    interview_mode = db.Column(db.String(30), default='online')  # online or offline
    interview_link = db.Column(db.String(500))    # zoom/meet link if online
    round_name = db.Column(db.String(100))        # e.g. Technical Round, HR Round
    remarks = db.Column(db.Text)

    application = db.relationship('Application', back_populates='interview')

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_time': self.interview_time,
            'interview_mode': self.interview_mode,
            'interview_link': self.interview_link,
            'round_name': self.round_name,
            'remarks': self.remarks
        }
