from datetime import datetime, timezone
from models import db

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(150), nullable=False)
    package = db.Column(db.String(50))        # salary package offered
    eligibility = db.Column(db.Text)          # eligibility requirements
    openings = db.Column(db.Integer, default=1)
    deadline = db.Column(db.Date)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default='pending')  # pending, approved, open, closed, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade='all, delete-orphan')

    def to_dict(self, with_company=True):
        drive_info = {}
        drive_info['id'] = self.id
        drive_info['company_id'] = self.company_id
        drive_info['title'] = self.title
        drive_info['job_role'] = self.job_role
        drive_info['package'] = self.package
        drive_info['eligibility'] = self.eligibility
        drive_info['openings'] = self.openings
        drive_info['deadline'] = self.deadline.isoformat() if self.deadline else None
        drive_info['description'] = self.description
        drive_info['status'] = self.status
        drive_info['created_at'] = self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        drive_info['applications_count'] = len(self.applications) if self.applications else 0
        
        # Optionally merge company details
        linked_company = self.company
        if with_company and linked_company:
            drive_info['company_name'] = linked_company.company_name
            drive_info['industry'] = linked_company.industry
            
        return drive_info

