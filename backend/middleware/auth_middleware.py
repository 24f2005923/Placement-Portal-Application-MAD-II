from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from exceptions import Unauthorized, Forbidden


def role_required(role_name):
    """
    Authorization decorator factory.

    Separates the two distinct failure cases according to HTTP semantics:
      401 Unauthorized — token is absent, expired, or cryptographically invalid.
      403 Forbidden    — token is valid but the bearer holds the wrong role.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                # JWT missing, expired, or tampered — identity cannot be established.
                raise Unauthorized('Authorization token is missing or invalid')

            jwt_payload = get_jwt()
            role_val = jwt_payload.get('role')

            if role_val != role_name:
                role_labels = {
                    'admin':   'Administrator privileges required',
                    'company': 'Company account required',
                    'student': 'Student account required'
                }
                label = role_labels.get(role_name, f'{role_name.capitalize()} account required')
                raise Forbidden(f'Access denied: {label}')

            return fn(*args, **kwargs)
        return wrapper
    return decorator


admin_required   = role_required('admin')
company_required = role_required('company')
student_required = role_required('student')
