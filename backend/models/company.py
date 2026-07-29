from models import db, DictMixin

class Company(db.Model, DictMixin):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    contact_person = db.Column(db.String(120))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='company')
    drives = db.relationship('PlacementDrive', back_populates='company', cascade='all, delete-orphan')

    @property
    def drive_ids(self):
        return [d.id for d in self.drives]

    @property
    def is_approved(self):
        return self.approval_status == 'approved' and not self.blacklisted

    def to_dict(self, show_drives=False):
        fields = [
            'id', 'user_id', 'company_name', 'industry', 'website', 'description',
            'contact_person', 'contact_email', 'contact_phone', 'city', 'address',
            'approval_status', 'blacklisted'
        ]
        data = self.as_dict(fields)
        data['drives_count'] = len(self.drives) if self.drives else 0
        
        linked_user = self.user
        if linked_user:
            data['email'] = linked_user.email
            data['status'] = linked_user.status
            
        if show_drives:
            data['drives'] = [drive.to_dict() for drive in self.drives]
            
        return data
