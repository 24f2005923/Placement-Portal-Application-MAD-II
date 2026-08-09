from models import db, DictMixin

class Interview(db.Model, DictMixin):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    interview_date = db.Column(db.Date)
    interview_time = db.Column(db.String(10))
    interview_mode = db.Column(db.String(30), default='online')  
    interview_link = db.Column(db.String(500))    
    round_name = db.Column(db.String(100))        
    remarks = db.Column(db.Text)

    application = db.relationship('Application', back_populates='interview')

    def to_dict(self):
        fields = [
            'id', 'application_id', 'interview_time', 'interview_mode',
            'interview_link', 'round_name', 'remarks'
        ]
        record = self.as_dict(fields)
        record['interview_date'] = self.interview_date.isoformat() if self.interview_date else None
        return record
