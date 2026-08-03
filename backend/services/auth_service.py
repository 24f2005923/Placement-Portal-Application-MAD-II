import logging
from sqlalchemy import func
from flask_jwt_extended import create_access_token, create_refresh_token
from models import db
from models.user import User
from models.student import Student
from models.company import Company
from exceptions import Forbidden, ValidationError, NotFound, Conflict
from utils.validators import validate_phone, validate_email, validate_password, check_required_fields

logger = logging.getLogger('auth_service')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [AUTH] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class AuthService:
    """
    Service handling authentication logic and JWT token generation for all roles.
    """

    @staticmethod
    def get_profile_id(user):
        """Resolves profile ID for student or company users."""
        if not user:
            return None
        if user.role == 'student' and user.student:
            return user.student.id
        elif user.role == 'company' and user.company:
            return user.company.id
        return None

    @staticmethod
    def create_user_tokens(user):
        """Generates JWT access and refresh tokens with user claims."""
        token_claims = {
            'role': user.role,
            'name': user.name
        }
        access_token = create_access_token(identity=str(user.id), additional_claims=token_claims)
        refresh_token = create_refresh_token(identity=str(user.id), additional_claims=token_claims)
        return access_token, refresh_token

    @classmethod
    def authenticate_user(cls, identifier, password, requested_role=None):
        """
        Validates credentials and checks account status.
        Returns: (user, response_data, status_code)
        """
        if not identifier or not str(identifier).strip() or not password:
            logger.warning("Authentication failed: Missing identifier or password")
            raise ValidationError("Email/Register number and password are required")

        clean_identifier = str(identifier).strip()
        lower_identifier = clean_identifier.lower()
        logger.info(f"Attempting login for identifier: {clean_identifier}")

        # Strategy 1: Lookup by Email (case-insensitive exact)
        matched_user = db.session.query(User).filter(func.lower(User.email) == lower_identifier).first()

        # Strategy 2: Fallback lookup by Student register_number (case-insensitive exact)
        if not matched_user:
            student_record = db.session.query(Student).filter(func.lower(Student.register_number) == lower_identifier).first()
            if student_record and student_record.user:
                matched_user = student_record.user

        # Strategy 3: Fallback lookup by User name (case-insensitive exact)
        if not matched_user:
            name_matched_user = db.session.query(User).filter(func.lower(User.name) == lower_identifier).first()
            if name_matched_user:
                matched_user = name_matched_user

        if not matched_user:
            logger.warning(f"No account matching identifier: {clean_identifier}")
            raise ValidationError("Invalid credentials")

        # Password verification
        if not matched_user.check_password(password):
            logger.warning(f"Incorrect password for User ID: {matched_user.id}")
            raise ValidationError("Invalid credentials")

        # Account active status check
        if matched_user.status == 'inactive':
            logger.warning(f"Account is deactivated for User ID: {matched_user.id}")
            raise Forbidden("Your account is deactivated. Please contact admin.")

        # Role mismatch check if a specific role was requested
        if requested_role and matched_user.role != requested_role:
            logger.warning(f"Role mismatch for User ID: {matched_user.id}. Expected {requested_role}, got {matched_user.role}")
            raise Forbidden(f"Access denied: This account is registered as a {matched_user.role.capitalize()}.")

        # Company specific validation
        if matched_user.role == 'company':
            associated_company = db.session.query(Company).filter(Company.user_id == matched_user.id).first()
            if associated_company:
                if associated_company.blacklisted:
                    logger.warning(f"Company ID {associated_company.id} is blacklisted")
                    raise Forbidden("Your company is blacklisted.")
                if associated_company.approval_status == 'pending':
                    logger.warning(f"Company ID {associated_company.id} approval pending")
                    raise Forbidden("Your company registration is still pending approval.")

        access_token, refresh_token = cls.create_user_tokens(matched_user)
        profile_id = cls.get_profile_id(matched_user)

        response_payload = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': matched_user.id,
                'name': matched_user.name,
                'email': matched_user.email,
                'role': matched_user.role,
                'profile_id': profile_id
            }
        }

        logger.info(f"Authentication successful for User ID: {matched_user.id} ({matched_user.role})")
        return matched_user, response_payload, 200

    @classmethod
    def register_student(cls, payload):
        """Validates payload and registers a new student user and profile."""
        req = ['name', 'email', 'password', 'register_number', 'department', 'year']
        check_required_fields(payload, req)

        target_email = validate_email(payload['email'])
        validated_pwd = validate_password(payload['password'])

        email_exists = db.session.query(User).filter(User.email == target_email).first()
        if email_exists:
            raise Conflict('This email is already registered')

        reg_number = payload['register_number'].strip()
        reg_exists = db.session.query(Student).filter(Student.register_number == reg_number).first()
        if reg_exists:
            raise Conflict('This register number already exists')

        # Build user
        user = User(name=payload['name'], email=target_email, role='student')
        user.set_password(validated_pwd)
        db.session.add(user)
        db.session.flush()

        # Build student profile
        student = Student(
            user_id=user.id,
            register_number=reg_number,
            department=payload['department'],
            year=payload.get('year', 4),
            phone=payload.get('phone'),
            cgpa=payload.get('cgpa', 0.0)
        )

        skills = payload.get('skills')
        if skills:
            student.save_skills(skills)

        db.session.add(student)
        db.session.commit()
        logger.info(f"Student account registered: {target_email}")
        return student.id

    @classmethod
    def register_company(cls, payload):
        """Validates payload and registers a new company user and profile."""
        req = ['company_name', 'email', 'password', 'industry', 'city', 'contact_email']
        check_required_fields(payload, req)

        target_email = validate_email(payload['email'])
        clean_phone = validate_phone(payload['phone'], field_name="Phone number")
        validated_pwd = validate_password(payload['password'])

        email_exists = db.session.query(User).filter(User.email == target_email).first()
        if email_exists:
            raise Conflict('This email is already registered')

        user = User(name=payload['company_name'], email=target_email, role='company')
        user.set_password(validated_pwd)
        db.session.add(user)
        db.session.flush()

        company = Company(
            user_id=user.id,
            company_name=payload['company_name'],
            industry=payload.get('industry'),
            contact_email=payload.get('contact_email', target_email),
            contact_phone=clean_phone,
            address=payload.get('address'),
            city=payload.get('city'),
            approval_status='pending'
        )
        db.session.add(company)
        db.session.commit()
        logger.info(f"Company account registered: {target_email}")
