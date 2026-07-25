from models import db

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
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    blacklisted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='company')
    drives = db.relationship('PlacementDrive', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self, show_drives=False):
        data = {}
        data['id'] = self.id
        data['user_id'] = self.user_id
        data['company_name'] = self.company_name
        data['industry'] = self.industry
        data['website'] = self.website
        data['description'] = self.description
        data['contact_person'] = self.contact_person
        data['contact_email'] = self.contact_email
        data['contact_phone'] = self.contact_phone
        data['city'] = self.city
        data['address'] = self.address
        data['approval_status'] = self.approval_status
        data['blacklisted'] = self.blacklisted
        data['drives_count'] = len(self.drives) if self.drives else 0
        
        # Add basic credentials if linked user exists
        linked_user = self.user
        if linked_user:
            data['email'] = linked_user.email
            data['status'] = linked_user.status
            
        if show_drives:
            drives_list = []
            for drive in self.drives:
                drives_list.append(drive.to_dict())
            data['drives'] = drives_list
            
        return data

