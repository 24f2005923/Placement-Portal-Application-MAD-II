from models import db
from models.user import User

# Admin configuration parameters
DEFAULT_ADMIN_EMAIL = 'admin@admin.com'
DEFAULT_ADMIN_PWD = 'password'
DEFAULT_ADMIN_NAME = 'Portal Admin'

def seed_admin():
    # Check for existing admin user using session queries
    existing_admin = db.session.query(User).filter(User.role == 'admin').first()
    
    # Check if the target email address is occupied
    email_holder = db.session.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()
    
    if email_holder is not None and email_holder.role != 'admin':
        print(f"Skipping admin seeding: Email {DEFAULT_ADMIN_EMAIL} is registered to a different role.")
        return

    # Initialize or reuse user object
    if existing_admin is None:
        if email_holder is not None:
            user_to_seed = email_holder
        else:
            user_to_seed = User(role='admin')
    else:
        user_to_seed = existing_admin

    # Apply admin values
    user_to_seed.name = DEFAULT_ADMIN_NAME
    user_to_seed.email = DEFAULT_ADMIN_EMAIL
    user_to_seed.role = 'admin'
    user_to_seed.status = 'active'
    user_to_seed.set_password(DEFAULT_ADMIN_PWD)

    # Save to db
    db.session.add(user_to_seed)
    db.session.commit()

    print("Administrator record verified/created.")
    print(f"Login: {DEFAULT_ADMIN_EMAIL} | Credentials: {DEFAULT_ADMIN_PWD}")

