
# Student model fields safe to update from user input.
STUDENT_PROFILE_FIELDS = [
    'department',
    'year',
    'cgpa',
    'phone',
    'address',
    'marks_10th',
    'marks_12th',
    'backlogs',
    'graduation_year',
    'preferred_role',
]


def apply_student_profile_fields(student, payload):
    """
    Update a student's profile fields from a request payload dictionary.

    Handles:
    - Standard student model fields (STUDENT_PROFILE_FIELDS list above)
    - User model name and email fields (via student.user)
    - Skills list (via student.save_skills())

    Only updates fields that are actually present in the payload —
    missing keys are silently skipped, so partial updates work correctly.

    Args:
        student: The Student model instance to update.
        payload:  A dict containing the new field values (from the API request).
    """
    from exceptions import ValidationError
    from utils.validators import validate_email, validate_phone, validate_department

    # Work on a mutable copy so we can normalise phone before the generic loop
    payload = dict(payload)

    if student.user:
        if 'name' in payload:
            name_val = str(payload['name']).strip()
            if len(name_val) < 2:
                raise ValidationError("Full name must be at least 2 characters")
            student.user.name = name_val
        if 'email' in payload and str(payload.get('email', '')).strip():
            student.user.email = validate_email(payload['email'])

    # Validate and normalise phone before the generic field loop
    if 'phone' in payload:
        phone_val = payload['phone']
        if phone_val and str(phone_val).strip():
            payload['phone'] = validate_phone(phone_val, field_name="Phone number")
        else:
            payload['phone'] = None

    # Validate CGPA range (0.0 – 10.0)
    if 'cgpa' in payload and payload['cgpa'] is not None and str(payload['cgpa']).strip() != '':
        try:
            cgpa_float = float(payload['cgpa'])
        except (ValueError, TypeError):
            raise ValidationError("CGPA must be a valid number")
        if not (0.0 <= cgpa_float <= 10.0):
            raise ValidationError("CGPA must be between 0.0 and 10.0")

    if 'department' in payload and str(payload.get('department', '')).strip():
        payload['department'] = validate_department(payload['department'])

    for field_name in STUDENT_PROFILE_FIELDS:
        if field_name in payload:
            setattr(student, field_name, payload[field_name])

    if 'skills' in payload:
        student.save_skills(payload['skills'])

