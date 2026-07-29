import logging
from models import db
from models.user import User

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_EMAIL = 'admin@admin.com'
DEFAULT_ADMIN_PWD = 'password'
DEFAULT_ADMIN_NAME = 'Portal Admin'

def seed_admin():
    """Seeds the default portal administrator account if it does not exist."""
    existing_admin = db.session.query(User).filter(User.role == 'admin').first()
    email_holder = db.session.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
    
    if email_holder is not None and email_holder.role != 'admin':
        logger.warning(f"Admin seeding skipped: Email {DEFAULT_ADMIN_EMAIL} belongs to a non-admin account.")
        return

    if existing_admin is None:
        user_to_seed = email_holder if email_holder is not None else User(role='admin')
    else:
        user_to_seed = existing_admin

    user_to_seed.name = DEFAULT_ADMIN_NAME
    user_to_seed.email = DEFAULT_ADMIN_EMAIL
    user_to_seed.role = 'admin'
    user_to_seed.status = 'active'
    user_to_seed.set_password(DEFAULT_ADMIN_PWD)

    db.session.add(user_to_seed)
    db.session.commit()

    logger.info("Administrator seed verification complete.")
