import logging
from sqlalchemy import func, or_
from flask_jwt_extended import create_access_token, create_refresh_token
from models import db
from models.user import User
from models.student import Student
from models.company import Company

# Set up dedicated auth logger
logger = logging.getLogger('auth_service')
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [AUTH] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class AuthService:
    """
    Generic, Production-Ready Authentication Service for all user roles (Student, Company, Admin).
    
    Robust Multi-Strategy Lookup Pipeline:
    1. Case-insensitive Email lookup (`User.email`)
    2. Case-insensitive Register Number lookup (`Student.register_number`)
    3. Case-insensitive Student Name lookup (`User.name`)
    4. Flexible Prefix / Typo Tolerance lookup (matches email local part or student name)
    
    Strict Pipeline Checks:
    - Input Validation
    - Account Resolution
    - Password Hash Verification (`check_password_hash`)
    - Account Active Status Check
    - Role Authorization & Company Approval Validation
    - JWT Generation & Student-Friendly Error Handling
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
        """Generates JWT access and refresh tokens with custom user claims."""
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
        Executes the generic authentication pipeline.
        Returns tuple: (user_object, response_dict, status_code)
        """
        logger.info("Pipeline Step 1: Validating request payload format")
        if not identifier or not str(identifier).strip() or not password:
            logger.warning("Authentication failed: Missing identifier or password")
            return None, {'error': 'Email/Register number and password are required parameters'}, 400

        clean_identifier = str(identifier).strip()
        lower_identifier = clean_identifier.lower()
        logger.info(f"Pipeline Step 2: Generic multi-field database lookup for identifier: '{clean_identifier}'")

        matched_user = None

        # Strategy 2a: Lookup by Email (case-insensitive exact)
        matched_user = db.session.query(User).filter(func.lower(User.email) == lower_identifier).first()
        if matched_user:
            logger.info(f"User resolved via User email '{matched_user.email}' -> User ID: {matched_user.id}")

        # Strategy 2b: Fallback lookup by Student register_number (case-insensitive exact)
        if matched_user is None:
            student_record = db.session.query(Student).filter(func.lower(Student.register_number) == lower_identifier).first()
            if student_record and student_record.user:
                matched_user = student_record.user
                logger.info(f"User resolved via Student register_number '{student_record.register_number}' -> User ID: {matched_user.id}")

        # Strategy 2c: Fallback lookup by User name (case-insensitive exact)
        if matched_user is None:
            name_matched_user = db.session.query(User).filter(func.lower(User.name) == lower_identifier).first()
            if name_matched_user:
                matched_user = name_matched_user
                logger.info(f"User resolved via User name '{matched_user.name}' -> User ID: {matched_user.id}")

        # Strategy 2d: Flexible Prefix / Typo Fallback (handles domain/spelling typos like adhithya@gmail.com vs adhithiya@gmail.com)
        if matched_user is None and '@' in lower_identifier:
            local_part = lower_identifier.split('@')[0]
            prefix_len = min(len(local_part), 5)
            if prefix_len >= 3:
                search_prefix = local_part[:prefix_len]
                candidates = db.session.query(User).filter(
                    or_(
                        func.lower(User.email).like(f"{search_prefix}%"),
                        func.lower(User.name).like(f"{search_prefix}%")
                    )
                ).all()
                if len(candidates) == 1:
                    matched_user = candidates[0]
                    logger.info(f"User resolved via flexible prefix candidate '{matched_user.email}' -> User ID: {matched_user.id}")

        if matched_user is None:
            logger.warning(f"Authentication failed: No account matching identifier '{clean_identifier}'")
            return None, {
                'error': 'Invalid credentials. Account not found. Please check your Email Address or Register Number.'
            }, 401

        logger.info(f"Pipeline Step 3: Verifying password hash for User ID: {matched_user.id} ({matched_user.email})")
        # Step 3: Password verification via werkzeug.security check_password_hash
        if not matched_user.check_password(password):
            logger.warning(f"Authentication failed: Password verification failed for User ID: {matched_user.id}")
            return None, {
                'error': 'Invalid credentials. Password incorrect. Please check your password.'
            }, 401

        logger.info(f"Pipeline Step 4: Checking account status for User ID: {matched_user.id}")
        # Step 4: Account active status check
        if matched_user.status == 'inactive':
            logger.warning(f"Authentication failed: Account inactive for User ID: {matched_user.id}")
            return None, {
                'error': 'Your account is deactivated. Please contact admin.'
            }, 403

        logger.info(f"Pipeline Step 5: Validating role and account constraints (Actual Role: {matched_user.role})")
        # Step 5a: Role mismatch check if a specific role was requested
        if requested_role and matched_user.role != requested_role:
            logger.warning(f"Authentication failed: Role mismatch. Actual: '{matched_user.role}', Requested: '{requested_role}'")
            return None, {
                'error': f'Access denied: This account is registered as a {matched_user.role.capitalize()}, not a {requested_role.capitalize()}.'
            }, 403

        # Step 5b: Company specific checks (blacklisted / approval pending)
        if matched_user.role == 'company':
            associated_company = db.session.query(Company).filter(Company.user_id == matched_user.id).first()
            if associated_company:
                if associated_company.blacklisted:
                    logger.warning(f"Authentication failed: Company ID {associated_company.id} is blacklisted")
                    return None, {'error': 'Your company is blacklisted'}, 403
                if associated_company.approval_status == 'pending':
                    logger.warning(f"Authentication failed: Company ID {associated_company.id} approval pending")
                    return None, {'error': 'Your company registration is still pending approval'}, 403

        logger.info(f"Pipeline Step 6: Generating JWT tokens for User ID: {matched_user.id}")
        # Step 6: Token generation & response payload assembly
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

        logger.info(f"Pipeline Step 7: Authentication successful for User ID: {matched_user.id} ({matched_user.role})")
        return matched_user, response_payload, 200
