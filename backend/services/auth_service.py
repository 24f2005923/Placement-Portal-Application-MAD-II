import logging
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
    Generic Authentication Service for all user roles (Student, Company, Admin).
    Provides modular pipeline for:
    - Input payload validation
    - Database lookup (by email or student register number)
    - Secure password hash verification
    - User account status and role authorization
    - JWT token generation and response payload formatting
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
            return None, {'error': 'Email/Register number and password are required'}, 400

        clean_identifier = str(identifier).strip()
        logger.info(f"Pipeline Step 2: Database lookup for identifier: '{clean_identifier}'")

        # Step 2a: Lookup by email (case-insensitive)
        matched_user = db.session.query(User).filter(User.email == clean_identifier.lower()).first()

        # Step 2b: Fallback lookup by Student register_number if not found by email
        if matched_user is None:
            logger.info("Identifier not found in User email column; attempting Student register_number lookup")
            student_record = db.session.query(Student).filter(Student.register_number == clean_identifier).first()
            if student_record and student_record.user:
                matched_user = student_record.user
                logger.info(f"User resolved via Student register_number '{clean_identifier}' -> User ID: {matched_user.id}")

        if matched_user is None:
            logger.warning(f"Authentication failed: No account matching identifier '{clean_identifier}'")
            return None, {'error': 'Invalid credentials'}, 401

        logger.info(f"Pipeline Step 3: Verifying password hash for User ID: {matched_user.id} ({matched_user.email})")
        # Step 3: Password verification via werkzeug.security check_password_hash
        if not matched_user.check_password(password):
            logger.warning(f"Authentication failed: Password verification failed for User ID: {matched_user.id}")
            return None, {'error': 'Invalid credentials'}, 401

        logger.info(f"Pipeline Step 4: Checking account status for User ID: {matched_user.id}")
        # Step 4: Account active status check
        if matched_user.status == 'inactive':
            logger.warning(f"Authentication failed: Account inactive for User ID: {matched_user.id}")
            return None, {'error': 'Your account is deactivated. Please contact admin.'}, 403

        logger.info(f"Pipeline Step 5: Validating role and account constraints (Role: {matched_user.role})")
        # Step 5a: Role mismatch check if a specific role was requested
        if requested_role and matched_user.role != requested_role:
            logger.warning(f"Authentication failed: Role mismatch. Actual: '{matched_user.role}', Requested: '{requested_role}'")
            return None, {'error': f'Access denied: This portal is for {requested_role} accounts only'}, 403

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
