
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
    if student.user:
        if 'name' in payload:
            student.user.name = payload['name']
        if 'email' in payload:
            student.user.email = str(payload['email']).lower().strip()

    for field_name in STUDENT_PROFILE_FIELDS:
        if field_name in payload:
            setattr(student, field_name, payload[field_name])

    if 'skills' in payload:
        student.save_skills(payload['skills'])
