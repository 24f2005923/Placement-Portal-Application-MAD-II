from werkzeug.security import generate_password_hash, check_password_hash
from models import db, TimestampMixin, DictMixin

class User(db.Model, TimestampMixin, DictMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)      # admin, student, company
    status = db.Column(db.String(20), default='active')  # active, inactive

    student = db.relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password_text):
        self.password_hash = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password_hash, password_text)

    @property
    def is_active(self):
        return self.status == 'active'

    def to_dict(self):
        res = self.as_dict(['id', 'name', 'email', 'role', 'status'])
        res['created_at'] = self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        return res
