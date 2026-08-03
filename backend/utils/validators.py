import re
from exceptions import ValidationError
from datetime import date

def validate_phone(phone, field_name="Phone number"):
    """
    Validates that the provided phone number consists of exactly 10 numeric digits.
    Raises ValidationError if missing or invalid.
    """
    if phone is None or str(phone).strip() == "":
        raise ValidationError(f"{field_name} is required")
    
    clean_phone = str(phone).strip()
    if not re.fullmatch(r'\d{10}', clean_phone):
        raise ValidationError(f"{field_name} must be exactly 10 digits")
    
    return clean_phone

def validate_email(email):
    """
    Validates basic email format.
    Raises ValidationError if missing or invalid format.
    """
    if not email or not str(email).strip():
        raise ValidationError("Email is required")
    
    clean_email = str(email).strip().lower()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, clean_email):
        raise ValidationError("Invalid email address format")
    
    return clean_email

def validate_password(password, field_name="Password"):
    """
    Validates password strength according to security policy:
    - Minimum 8 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one numeric digit (0-9)
    - At least one special character
    Raises ValidationError if any condition fails.
    """
    if not password or not str(password).strip():
        raise ValidationError(f"{field_name} is required")
    
    pwd_str = str(password)
    
    if len(pwd_str) < 8:
        raise ValidationError(f"{field_name} must be at least 8 characters long")
    if not re.search(r'[A-Z]', pwd_str):
        raise ValidationError(f"{field_name} must contain at least one uppercase letter")
    if not re.search(r'[a-z]', pwd_str):
        raise ValidationError(f"{field_name} must contain at least one lowercase letter")
    if not re.search(r'[0-9]', pwd_str):
        raise ValidationError(f"{field_name} must contain at least one number")
    if not re.search(r'[^a-zA-Z0-9]', pwd_str):
        raise ValidationError(f"{field_name} must contain at least one special character")
    
    return pwd_str

def validate_status_choice(status, allowed, field_name="Status"):
    """Validates that a given status string is in the allowed list."""
    if not status or str(status).strip().lower() not in allowed:
        raise ValidationError(f"{field_name} must be one of: {', '.join(allowed)}")
    return str(status).strip().lower()

def validate_date_format(date_str, field_name="Date"):
    """Validates that a given string is a valid ISO format date (YYYY-MM-DD)."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(str(date_str).strip())
    except ValueError:
        raise ValidationError(f"{field_name} format should be YYYY-MM-DD")

def check_required_fields(payload, required_fields):
    """
    Checks if all required fields are present and not empty in the payload.
    Raises ValidationError if any are missing.
    """
    missing = [f for f in required_fields if not str(payload.get(f, '')).strip()]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")
