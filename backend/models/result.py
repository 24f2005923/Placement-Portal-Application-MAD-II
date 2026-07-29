from datetime import datetime, timezone
from models import db, DictMixin

class Result(db.Model, DictMixin):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, unique=True)
    result_status = db.Column(db.String(20), nullable=False)  # selected or rejected
    remarks = db.Column(db.Text)
    published_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    application = db.relationship('Application', back_populates='result')

    def to_dict(self):
        fields = ['id', 'application_id', 'result_status', 'remarks']
        res = self.as_dict(fields)
        res['published_at'] = self.published_at.strftime('%Y-%m-%d %H:%M') if self.published_at else None
        return res
