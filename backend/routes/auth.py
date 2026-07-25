from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models import db
from models.user import User
from models.student import Student
from models.company import Company

auth_bp = Blueprint('auth_routes', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    if payload is None:
        return jsonify({'error': 'Request body is empty'}), 400

    email_input = payload.get('email', '').strip().lower()
    pwd_input = payload.get('password', '')

    if not email_input or not pwd_input:
        return jsonify({'error': 'Email and password are required parameters'}), 400

    # Retrieve user via session query
    matched_user = db.session.query(User).filter(User.email == email_input).first()

    if matched_user is None:
        return jsonify({'error': 'Invalid email or password'}), 401

    if not matched_user.check_password(pwd_input):
        return jsonify({'error': 'Invalid email or password'}), 401

    if matched_user.status == 'inactive':
        return jsonify({'error': 'Your account is deactivated. Please contact admin.'}), 403

    if matched_user.role == 'company':
        associated_company = db.session.query(Company).filter(Company.user_id == matched_user.id).first()
        if associated_company is not None:
            if associated_company.blacklisted:
                return jsonify({'error': 'Your company is blacklisted'}), 403
            if associated_company.approval_status == 'pending':
                return jsonify({'error': 'Your company registration is still pending approval'}), 403

    # Generate custom claims
    token_claims = {
        'role': matched_user.role,
        'name': matched_user.name
    }
    
    access_token = create_access_token(identity=str(matched_user.id), additional_claims=token_claims)
    refresh_token = create_refresh_token(identity=str(matched_user.id), additional_claims=token_claims)

    associated_profile_id = None
    if matched_user.role == 'student':
        if matched_user.student:
            associated_profile_id = matched_user.student.id
    elif matched_user.role == 'company':
        if matched_user.company:
            associated_profile_id = matched_user.company.id

    print(f"Logged in user: {matched_user.email}")

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': matched_user.id,
            'name': matched_user.name,
            'email': matched_user.email,
            'role': matched_user.role,
            'profile_id': associated_profile_id
        }
    }), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'No payload provided'}), 400

    # Validation
    required_inputs = ['name', 'email', 'password', 'register_number', 'department']
    missing_fields = []
    for input_key in required_inputs:
        if not payload.get(input_key):
            missing_fields.append(input_key)
            
    if missing_fields:
        fields_str = ', '.join(missing_fields)
        return jsonify({'error': f"Missing required fields: {fields_str}"}), 400

    target_email = payload['email'].strip().lower()

    # Query for duplicates
    email_exists = db.session.query(User).filter(User.email == target_email).first()
    if email_exists is not None:
        return jsonify({'error': 'This email is already registered'}), 409

    reg_number = payload['register_number']
    reg_exists = db.session.query(Student).filter(Student.register_number == reg_number).first()
    if reg_exists is not None:
        return jsonify({'error': 'This register number already exists'}), 409

    # Build new user account
    created_user = User(name=payload['name'], email=target_email, role='student')
    created_user.set_password(payload['password'])
    db.session.add(created_user)
    db.session.flush()

    # Build new student profile
    created_student = Student(
        user_id=created_user.id,
        register_number=reg_number,
        department=payload['department'],
        year=payload.get('year', 4),
        phone=payload.get('phone'),
        cgpa=payload.get('cgpa', 0.0)
    )

    submitted_skills = payload.get('skills')
    if submitted_skills:
        created_student.save_skills(submitted_skills)

    db.session.add(created_student)
    db.session.commit()

    print(f"Student account registered: {target_email}")

    return jsonify({
        'message': 'Student registered successfully',
        'student_id': created_student.id
    }), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'No data sent'}), 400

    required_inputs = ['company_name', 'email', 'password']
    missing_fields = []
    for input_key in required_inputs:
        if not payload.get(input_key):
            missing_fields.append(input_key)
            
    if missing_fields:
        fields_str = ', '.join(missing_fields)
        return jsonify({'error': f"Missing fields: {fields_str}"}), 400

    target_email = payload['email'].strip().lower()

    # Query duplicate email
    email_exists = db.session.query(User).filter(User.email == target_email).first()
    if email_exists is not None:
        return jsonify({'error': 'This email is already registered'}), 409

    # Build company user
    created_user = User(name=payload['company_name'], email=target_email, role='company')
    created_user.set_password(payload['password'])
    db.session.add(created_user)
    db.session.flush()

    # Build company profile
    created_company = Company(
        user_id=created_user.id,
        company_name=payload['company_name'],
        industry=payload.get('industry'),
        contact_email=payload.get('contact_email', target_email),
        contact_phone=payload.get('phone'),
        address=payload.get('address'),
        city=payload.get('city'),
        approval_status='pending'
    )
    
    db.session.add(created_company)
    db.session.commit()

    print(f"Company account registered: {target_email}")

    return jsonify({
        'message': 'Company registered. Waiting for admin approval.'
    }), 201

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    active_identity = get_jwt_identity()
    token_claims = get_jwt()

    refreshed_claims = {
        'role': token_claims.get('role'),
        'name': token_claims.get('name')
    }
    
    new_access_token = create_access_token(identity=active_identity, additional_claims=refreshed_claims)
    return jsonify({'access_token': new_access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    active_identity = int(get_jwt_identity())
    user_record = db.session.query(User).filter(User.id == active_identity).first()
    
    if user_record is None:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({'user': user_record.to_dict()}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Logout confirmation response
    return jsonify({'message': 'Logged out successfully'}), 200

