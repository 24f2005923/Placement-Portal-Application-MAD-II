import json
from models import db


# Student table - stores academic details and profile of each student
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, default=4)
    cgpa = db.Column(db.Float, default=0.0)
    skills = db.Column(db.Text, default='[]')   # stored as json string in db
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    resume_path = db.Column(db.String(256))
    placement_status = db.Column(db.String(30), default='Not Placed')
    marks_10th = db.Column(db.Float)
    marks_12th = db.Column(db.Float)
    backlogs = db.Column(db.Integer, default=0)
    graduation_year = db.Column(db.Integer)
    preferred_role = db.Column(db.String(100))

    user = db.relationship('User', back_populates='student')
    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')

    # helper to get skills as a python list
    def get_skills(self):
        try:
            return json.loads(self.skills)
        except Exception:
            return []

    # helper to save skills - accepts list or comma string
    def save_skills(self, value):
        if isinstance(value, list):
            self.skills = json.dumps(value)
        elif isinstance(value, str):
            skill_list = [s.strip() for s in value.split(',') if s.strip()]
            self.skills = json.dumps(skill_list)
        else:
            self.skills = '[]'

    def to_dict(self):
        student_data = {
            'id': self.id,
            'user_id': self.user_id,
            'register_number': self.register_number,
            'department': self.department,
            'year': self.year,
            'cgpa': self.cgpa,
            'skills': self.get_skills(),
            'phone': self.phone,
            'address': self.address,
            'resume_path': self.resume_path,
            'placement_status': self.placement_status,
            'marks_10th': self.marks_10th,
            'marks_12th': self.marks_12th,
            'backlogs': self.backlogs,
            'graduation_year': self.graduation_year,
            'preferred_role': self.preferred_role
        }
        # also include user name and email if user exists
        if self.user:
            student_data['name'] = self.user.name
            student_data['email'] = self.user.email
            student_data['status'] = self.user.status
        return student_data
