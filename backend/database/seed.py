import logging
from models import db
from models.user import User

logger = logging.getLogger(__name__)

def seed_admin():
    """Create the initial administrator account only when no admin exists."""
    from flask import current_app

    if not current_app.config.get('SEED_ADMIN', True):
        logger.info("Administrator bootstrap disabled by SEED_ADMIN=false.")
        return

    existing_admin = db.session.query(User).filter(User.role == 'admin').first()
    if existing_admin is not None:
        logger.info("Administrator bootstrap skipped because an admin already exists.")
        return

    admin_email = current_app.config['DEFAULT_ADMIN_EMAIL'].lower().strip()
    email_holder = db.session.query(User).filter(User.email == admin_email).first()
    if email_holder is not None:
        logger.warning("Administrator bootstrap skipped: %s belongs to a non-admin account.", admin_email)
        return

    user_to_seed = User(
        name=current_app.config['DEFAULT_ADMIN_NAME'],
        email=admin_email,
        role='admin',
        status='active',
    )
    user_to_seed.set_password(current_app.config['DEFAULT_ADMIN_PASSWORD'])

    db.session.add(user_to_seed)
    db.session.commit()

    logger.info("Initial administrator account created.")
