from datetime import datetime
from models import db


# PlacementDrive table - each row is one job drive posted by a company
class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(150), nullable=False)
    package = db.Column(db.String(50))        # salary package offered
    eligibility = db.Column(db.Text)          # eligibility criteria text
    openings = db.Column(db.Integer, default=1)
    deadline = db.Column(db.Date)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default='pending')  # pending / approved / open / closed / rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade='all, delete-orphan')

    def to_dict(self, with_company=True):
        drive_data = {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'job_role': self.job_role,
            'package': self.package,
            'eligibility': self.eligibility,
            'openings': self.openings,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            'applications_count': len(self.applications) if self.applications else 0
        }
        # add company name and industry if needed
        if with_company and self.company:
            drive_data['company_name'] = self.company.company_name
            drive_data['industry'] = self.company.industry
        return drive_data
