from datetime import date
from models import db, TimestampMixin, DictMixin

class PlacementDrive(db.Model, TimestampMixin, DictMixin):
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

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade='all, delete-orphan')

    @property
    def days_until_deadline(self):
        if not self.deadline:
            return None
        diff = self.deadline - date.today()
        return max(0, diff.days)

    @property
    def is_accepting_applications(self):
        if self.status != 'open':
            return False
        if self.deadline and date.today() > self.deadline:
            return False
        return True

    def to_dict(self, with_company=True):
        fields = [
            'id', 'company_id', 'title', 'job_role', 'package', 'eligibility',
            'openings', 'description', 'status'
        ]
        drive_info = self.as_dict(fields)
        drive_info['deadline'] = self.deadline.isoformat() if self.deadline else None
        drive_info['created_at'] = self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        drive_info['applications_count'] = len(self.applications) if self.applications else 0
        drive_info['days_until_deadline'] = self.days_until_deadline
        drive_info['is_active'] = self.is_accepting_applications
        
        linked_company = self.company
        if with_company and linked_company:
            drive_info['company_name'] = linked_company.company_name
            drive_info['industry'] = linked_company.industry
            
        return drive_info
