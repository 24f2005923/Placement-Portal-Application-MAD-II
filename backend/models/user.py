from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)      # admin, student, company
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password_text):
        self.password_hash = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password_hash, password_text)

    def to_dict(self):
        user_info = {}
        user_info['id'] = self.id
        user_info['name'] = self.name
        user_info['email'] = self.email
        user_info['role'] = self.role
        user_info['status'] = self.status
        user_info['created_at'] = self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        return user_info

