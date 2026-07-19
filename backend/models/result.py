from datetime import datetime
from models import db


# Result table - stores the final selection/rejection result for each application
class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    result_status = db.Column(db.String(20), nullable=False)  # selected or rejected
    remarks = db.Column(db.Text)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship('Application', back_populates='result')

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'result_status': self.result_status,
            'remarks': self.remarks,
            'published_at': self.published_at.strftime('%Y-%m-%d %H:%M') if self.published_at else None
        }
