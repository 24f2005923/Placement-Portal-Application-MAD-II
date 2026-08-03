"""
student_updater.py — Shared student profile field update helper
─────────────────────────────────────────────────────────────────
Both AdminService.update_student() and StudentService.update_profile()
need to update the same set of student model fields from a request payload.
This module provides a single, reusable function so that list is never
duplicated and any future field additions only need one change.
"""

# These are the student model fields that are safe to update from user input.
# 'name' and 'email' are on the related User model and handled separately.
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
    # Update user-level fields (name and email live on the related User model)
    if student.user:
        if 'name' in payload:
            student.user.name = payload['name']
        if 'email' in payload:
            student.user.email = str(payload['email']).lower().strip()

    # Update student model fields from the shared field list
    for field_name in STUDENT_PROFILE_FIELDS:
        if field_name in payload:
            setattr(student, field_name, payload[field_name])

    # Skills are stored as a JSON string — use the model's helper method
    if 'skills' in payload:
        student.save_skills(payload['skills'])
