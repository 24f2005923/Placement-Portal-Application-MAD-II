from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


# These are decorator functions to protect routes based on user role.
# We add these on top of any route function that needs login.

# Use this on routes that only admin can access
def admin_required(f):
    @wraps(f)
    def check_if_admin(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Please login to access this page'}), 401

        token_data = get_jwt()
        user_role = token_data.get('role')

        if user_role != 'admin':
            return jsonify({'error': 'Only admin can access this'}), 403

        return f(*args, **kwargs)
    return check_if_admin


# Use this on routes that only company users can access
def company_required(f):
    @wraps(f)
    def check_if_company(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Please login to access this page'}), 401

        token_data = get_jwt()
        user_role = token_data.get('role')

        if user_role != 'company':
            return jsonify({'error': 'Only company accounts can access this'}), 403

        return f(*args, **kwargs)
    return check_if_company


# Use this on routes that only students can access
def student_required(f):
    @wraps(f)
    def check_if_student(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Please login to access this page'}), 401

        token_data = get_jwt()
        user_role = token_data.get('role')

        if user_role != 'student':
            return jsonify({'error': 'Only students can access this'}), 403

        return f(*args, **kwargs)
    return check_if_student
