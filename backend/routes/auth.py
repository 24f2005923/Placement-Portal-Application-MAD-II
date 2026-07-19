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

# auth blueprint handles login, register, logout
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# LOGIN - POST /api/auth/login
@auth_bp.route('/login', methods=['POST'])
def login():
    # get json data from request
    req_data = request.get_json()

    if not req_data:
        return jsonify({'error': 'No data received'}), 400

    user_email = req_data.get('email', '').strip().lower()
    user_password = req_data.get('password', '')

    # check both fields are filled
    if not user_email or not user_password:
        return jsonify({'error': 'Email and password are required'}), 400

    # find the user in database
    user = User.query.filter_by(email=user_email).first()

    # user not found
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    # check password
    if not user.check_password(user_password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # check if account is active
    if user.status == 'inactive':
        return jsonify({'error': 'Your account is deactivated. Please contact admin.'}), 403

    # if user is a company, check if they are approved
    if user.role == 'company':
        company = Company.query.filter_by(user_id=user.id).first()
        if company:
            if company.blacklisted:
                return jsonify({'error': 'Your company is blacklisted'}), 403
            if company.approval_status == 'pending':
                return jsonify({'error': 'Your company registration is still pending approval'}), 403

    # create tokens with user info embedded
    token_claims = {'role': user.role, 'name': user.name}
    access_token = create_access_token(identity=str(user.id), additional_claims=token_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=token_claims)

    # get the profile id (student or company id)
    profile_id = None
    if user.role == 'student' and user.student:
        profile_id = user.student.id
    elif user.role == 'company' and user.company:
        profile_id = user.company.id

    print('Login successful for:', user.email)  # for debugging

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'profile_id': profile_id
        }
    }), 200


# STUDENT REGISTRATION - POST /api/auth/register/student
@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    req_data = request.get_json()

    if not req_data:
        return jsonify({'error': 'No data provided'}), 400

    # check required fields
    required_fields = ['name', 'email', 'password', 'register_number', 'department']
    missing = []
    for field in required_fields:
        if not req_data.get(field):
            missing.append(field)

    if missing:
        return jsonify({'error': 'Missing required fields: ' + ', '.join(missing)}), 400

    email = req_data['email'].strip().lower()

    # check email not already used
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'This email is already registered'}), 409

    # check register number not already used
    if Student.query.filter_by(register_number=req_data['register_number']).first():
        return jsonify({'error': 'This register number already exists'}), 409

    # create the user account
    new_user = User(name=req_data['name'], email=email, role='student')
    new_user.set_password(req_data['password'])
    db.session.add(new_user)
    db.session.flush()  # flush to get the user id before committing

    # create the student profile
    new_student = Student(
        user_id=new_user.id,
        register_number=req_data['register_number'],
        department=req_data['department'],
        year=req_data.get('year', 4),
        phone=req_data.get('phone'),
        cgpa=req_data.get('cgpa', 0.0)
    )

    # save skills if provided
    if req_data.get('skills'):
        new_student.save_skills(req_data['skills'])

    db.session.add(new_student)
    db.session.commit()

    print('New student registered:', email)

    return jsonify({'message': 'Student registered successfully', 'student_id': new_student.id}), 201


# COMPANY REGISTRATION - POST /api/auth/register/company
@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    req_data = request.get_json()

    if not req_data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['company_name', 'email', 'password']
    missing = []
    for field in required_fields:
        if not req_data.get(field):
            missing.append(field)

    if missing:
        return jsonify({'error': 'Missing fields: ' + ', '.join(missing)}), 400

    email = req_data['email'].strip().lower()

    # check if email is already registered
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'This email is already registered'}), 409

    # create user account for company
    new_user = User(name=req_data['company_name'], email=email, role='company')
    new_user.set_password(req_data['password'])
    db.session.add(new_user)
    db.session.flush()

    # create company profile
    new_company = Company(
        user_id=new_user.id,
        company_name=req_data['company_name'],
        industry=req_data.get('industry'),
        contact_email=req_data.get('contact_email', email),
        contact_phone=req_data.get('phone'),
        address=req_data.get('address'),
        city=req_data.get('city'),
        approval_status='pending'   # needs admin approval
    )
    db.session.add(new_company)
    db.session.commit()

    print('New company registered:', email)

    return jsonify({'message': 'Company registered. Waiting for admin approval.'}), 201


# REFRESH TOKEN - POST /api/auth/refresh
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    old_claims = get_jwt()

    # carry forward the role and name in new token
    new_claims = {
        'role': old_claims.get('role'),
        'name': old_claims.get('name')
    }
    new_access_token = create_access_token(identity=user_id, additional_claims=new_claims)

    return jsonify({'access_token': new_access_token}), 200


# GET CURRENT USER INFO - GET /api/auth/me
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()}), 200


# LOGOUT - POST /api/auth/logout
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # in a real app we would blacklist the token here
    # for now just returning success
    return jsonify({'message': 'Logged out successfully'}), 200
