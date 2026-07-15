from models.user import User
from models import db


# Static admin credentials for the portal
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASSWORD = 'password'
ADMIN_NAME = 'Portal Admin'


# This function creates or updates the default admin account on startup
def seed_admin():
    # prefer the existing admin record if one is present
    admin_user = User.query.filter_by(role='admin').first()

    # if another account already uses the static email, only reuse it when it is the admin account
    email_owner = User.query.filter_by(email=ADMIN_EMAIL).first()
    if email_owner and email_owner.role != 'admin':
        print('Admin seed skipped: ' + ADMIN_EMAIL + ' is already used by a non-admin account')
        return

    if not admin_user:
        admin_user = email_owner or User(role='admin')

    admin_user.name = ADMIN_NAME
    admin_user.email = ADMIN_EMAIL
    admin_user.role = 'admin'
    admin_user.status = 'active'
    admin_user.set_password(ADMIN_PASSWORD)

    db.session.add(admin_user)
    db.session.commit()

    print('Admin account created successfully')
    print('Login: admin@admin.com | Password: password')
