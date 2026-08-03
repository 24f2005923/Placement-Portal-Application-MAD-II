from flask import Blueprint, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models import db
from models.user import User
from services.auth_service import AuthService
from exceptions import NotFound
from utils.request_helpers import json_payload
from utils.responses import success_response, created_response

auth_bp = Blueprint('auth_routes', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    payload = json_payload()
    identifier = payload.get('email') or payload.get('register_no') or payload.get('register_number') or payload.get('identifier', '')
    pwd_input = payload.get('password', '')
    requested_role = payload.get('role')

    _, res_data, status_code = AuthService.authenticate_user(
        identifier=identifier,
        password=pwd_input,
        requested_role=requested_role
    )

    return jsonify(res_data), status_code

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    payload = json_payload()
    student_id = AuthService.register_student(payload)
    return created_response({'student_id': student_id}, 'Student registered successfully')

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    payload = json_payload()
    AuthService.register_company(payload)
    return created_response(message='Company registered. Waiting for admin approval.')

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
    return success_response({'access_token': new_access_token})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    active_identity = int(get_jwt_identity())
    user_record = db.session.query(User).filter(User.id == active_identity).first()
    
    if user_record is None:
        raise NotFound('User not found')
        
    return success_response({'user': user_record.to_dict()})

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return success_response(message='Logged out successfully')
