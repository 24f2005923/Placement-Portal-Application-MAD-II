from models import db

class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    interview_date = db.Column(db.Date)
    interview_time = db.Column(db.String(10))
    interview_mode = db.Column(db.String(30), default='online')  # online / offline
    interview_link = db.Column(db.String(500))    # link if online
    round_name = db.Column(db.String(100))        # round title
    remarks = db.Column(db.Text)

    application = db.relationship('Application', back_populates='interview')

    def to_dict(self):
        record = {}
        record['id'] = self.id
        record['application_id'] = self.application_id
        record['interview_date'] = self.interview_date.isoformat() if self.interview_date else None
        record['interview_time'] = self.interview_time
        record['interview_mode'] = self.interview_mode
        record['interview_link'] = self.interview_link
        record['round_name'] = self.round_name
        record['remarks'] = self.remarks
        return record

