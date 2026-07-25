from datetime import datetime, timezone
from models import db

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    result_status = db.Column(db.String(20), nullable=False)  # selected or rejected
    remarks = db.Column(db.Text)
    published_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    application = db.relationship('Application', back_populates='result')

    def to_dict(self):
        res = {}
        res['id'] = self.id
        res['application_id'] = self.application_id
        res['result_status'] = self.result_status
        res['remarks'] = self.remarks
        res['published_at'] = self.published_at.strftime('%Y-%m-%d %H:%M') if self.published_at else None
        return res

