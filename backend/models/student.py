import json
from models import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, default=4)
    cgpa = db.Column(db.Float, default=0.0)
    skills = db.Column(db.Text, default='[]')   # json list representation

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

    # fetch skills as py list
    def get_skills(self):
        try:
            return json.loads(self.skills or '[]')
        except (TypeError, ValueError):
            return []

    # update skills column from input
    def save_skills(self, input_val):
        if isinstance(input_val, list):
            self.skills = json.dumps(input_val)
        elif isinstance(input_val, str):
            parts = input_val.split(',')
            cleaned_skills = []
            for part in parts:
                cleaned = part.strip()
                if cleaned:
                    cleaned_skills.append(cleaned)
            self.skills = json.dumps(cleaned_skills)
        else:
            self.skills = '[]'

    def to_dict(self):
        profile = {}
        profile['id'] = self.id
        profile['user_id'] = self.user_id
        profile['register_number'] = self.register_number
        profile['department'] = self.department
        profile['year'] = self.year
        profile['cgpa'] = self.cgpa
        profile['skills'] = self.get_skills()
        profile['phone'] = self.phone
        profile['address'] = self.address
        profile['resume_path'] = self.resume_path
        profile['placement_status'] = self.placement_status
        profile['marks_10th'] = self.marks_10th
        profile['marks_12th'] = self.marks_12th
        profile['backlogs'] = self.backlogs
        profile['graduation_year'] = self.graduation_year
        profile['preferred_role'] = self.preferred_role
        
        # Merge linked User attributes if present
        linked_user = self.user
        if linked_user:
            profile['name'] = linked_user.name
            profile['email'] = linked_user.email
            profile['status'] = linked_user.status
            
        return profile

