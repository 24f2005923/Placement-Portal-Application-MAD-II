from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


# User table - every person who logs in (admin, student, company) has a row here
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)      # admin / student / company
    status = db.Column(db.String(20), default='active')  # active / inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # each user can have either a student profile or company profile
    student = db.relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')

    # hash and save password - we never store plain text password
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    # check entered password against stored hash
    def check_password(self, raw_password):
        result = check_password_hash(self.password_hash, raw_password)
        return result

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }
