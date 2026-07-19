from models import db


# Company table - stores company details and approval status
class Company(db.Model):
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
    approval_status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='company')
    drives = db.relationship('PlacementDrive', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self, show_drives=False):
        info = {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'website': self.website,
            'description': self.description,
            'contact_person': self.contact_person,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'city': self.city,
            'address': self.address,
            'approval_status': self.approval_status,
            'blacklisted': self.blacklisted,
            'drives_count': len(self.drives) if self.drives else 0
        }
        if self.user:
            info['email'] = self.user.email
            info['status'] = self.user.status
        # include list of drives if needed
        if show_drives:
            info['drives'] = [d.to_dict() for d in self.drives]
        return info
