from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_required(fn):
    @wraps(fn)
    def enforce_admin(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Authorization token is missing or invalid'}), 401
            
        jwt_payload = get_jwt()
        role_val = jwt_payload.get('role')
        
        if role_val != 'admin':
            return jsonify({'error': 'Access denied: Administrator privileges required'}), 403
            
        return fn(*args, **kwargs)
    return enforce_admin

def company_required(fn):
    @wraps(fn)
    def enforce_company(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Authorization token is missing or invalid'}), 401
            
        jwt_payload = get_jwt()
        role_val = jwt_payload.get('role')
        
        if role_val != 'company':
            return jsonify({'error': 'Access denied: Company account required'}), 403
            
        return fn(*args, **kwargs)
    return enforce_company

def student_required(fn):
    @wraps(fn)
    def enforce_student(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Authorization token is missing or invalid'}), 401
            
        jwt_payload = get_jwt()
        role_val = jwt_payload.get('role')
        
        if role_val != 'student':
            return jsonify({'error': 'Access denied: Student account required'}), 403
            
        return fn(*args, **kwargs)
    return enforce_student

