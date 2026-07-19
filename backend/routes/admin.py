from flask import Blueprint, request, jsonify, send_from_directory
from middleware.auth_middleware import admin_required
from models import db
from models.user import User
from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.result import Result

# all admin routes are under /api/admin
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ---- DASHBOARD ----

# get overall stats for admin dashboard
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    total_students = Student.query.count()
    total_companies = Company.query.filter_by(blacklisted=False).count()

    # count drives that are currently open or approved
    active_drives = PlacementDrive.query.filter(
        PlacementDrive.status.in_(['open', 'approved'])
    ).count()

    placed_count = Student.query.filter_by(placement_status='Placed').count()

    stats_list = [
        {'label': 'Total Students', 'value': str(total_students), 'icon': 'bi-people', 'tone': 'primary'},
        {'label': 'Total Companies', 'value': str(total_companies), 'icon': 'bi-buildings', 'tone': 'success'},
        {'label': 'Active Drives', 'value': str(active_drives), 'icon': 'bi-megaphone', 'tone': 'warning'},
        {'label': 'Placed Students', 'value': str(placed_count), 'icon': 'bi-award', 'tone': 'danger'}
    ]

    return jsonify({'stats': stats_list}), 200


# get recent activity for admin dashboard
@admin_bp.route('/activities', methods=['GET'])
@admin_required
def get_recent_activities():
    activities = []

    # get last 3 applications
    recent_apps = Application.query.order_by(Application.applied_at.desc()).limit(3).all()
    for app in recent_apps:
        student_name = ''
        if app.student and app.student.user:
            student_name = app.student.user.name
        drive_title = app.drive.title if app.drive else 'Unknown'
        activities.append({
            'title': student_name + ' applied for ' + drive_title,
            'meta': app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else '',
            'tone': 'primary'
        })

    # show pending company approvals
    pending_companies = Company.query.filter_by(approval_status='pending').count()
    if pending_companies > 0:
        activities.append({
            'title': str(pending_companies) + ' company registration(s) need approval',
            'meta': 'Pending',
            'tone': 'danger'
        })

    # show pending drive approvals
    pending_drives = PlacementDrive.query.filter_by(status='pending').count()
    if pending_drives > 0:
        activities.append({
            'title': str(pending_drives) + ' placement drive(s) waiting for approval',
            'meta': 'Pending',
            'tone': 'warning'
        })

    return jsonify({'activities': activities}), 200


# ---- REPORTS ----

@admin_bp.route('/reports/stats', methods=['GET'])
@admin_required
def get_report_stats():
    total_students = Student.query.count()
    placed = Student.query.filter_by(placement_status='Placed').count()

    # calculate placement percentage
    if total_students > 0:
        placement_rate = round((placed / total_students) * 100, 1)
    else:
        placement_rate = 0

    total_drives = PlacementDrive.query.count()
    approved_drives = PlacementDrive.query.filter(
        PlacementDrive.status.in_(['open', 'approved', 'closed'])
    ).count()

    if total_drives > 0:
        drive_conversion = round((approved_drives / total_drives) * 100, 1)
    else:
        drive_conversion = 0

    total_apps = Application.query.count()
    selected_apps = Application.query.filter_by(application_status='selected').count()

    if total_apps > 0:
        interview_success = round((selected_apps / total_apps) * 100, 1)
    else:
        interview_success = 0

    return jsonify({
        'stats': [
            {'label': 'Placement Rate', 'value': str(placement_rate) + '%', 'icon': 'bi-graph-up', 'tone': 'primary'},
            {'label': 'Drive Conversion', 'value': str(drive_conversion) + '%', 'icon': 'bi-arrow-repeat', 'tone': 'success'},
            {'label': 'Average Package', 'value': 'N/A', 'icon': 'bi-currency-rupee', 'tone': 'warning'},
            {'label': 'Interview Success', 'value': str(interview_success) + '%', 'icon': 'bi-person-check', 'tone': 'danger'}
        ]
    }), 200


# ---- SETTINGS ----
# storing settings as a simple dict for now
# TODO: move this to database table later

portal_settings = {
    'portal_name': 'University Placement Portal',
    'academic_year': '2025-26',
    'notification_email': 'admin@admin.com',
    'self_registration': True,
    'company_approvals': True,
    'instant_notifications': False
}


@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    return jsonify({'settings': portal_settings}), 200


@admin_bp.route('/settings', methods=['PUT'])
@admin_required
def update_settings():
    new_data = request.get_json()
    if new_data:
        portal_settings.update(new_data)
    return jsonify({'message': 'Settings updated', 'settings': portal_settings}), 200


# ---- STUDENTS ----

@admin_bp.route('/students', methods=['GET'])
@admin_required
def get_all_students():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = Student.query.join(User)

    # search by name, register number, or department
    if search:
        search_term = '%' + search + '%'
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                Student.register_number.ilike(search_term),
                Student.department.ilike(search_term)
            )
        )

    # filter by status
    if status_filter and status_filter.lower() != 'all':
        if status_filter.lower() == 'inactive':
            query = query.filter(User.status == 'inactive')
        else:
            query = query.filter(Student.placement_status.ilike(status_filter))

    total = query.count()
    students = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'students': [s.to_dict() for s in students],
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    }), 200


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@admin_required
def get_student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    data = student.to_dict()

    # also include placement history
    placement_history = []
    for app in student.applications:
        if app.result and app.result.result_status == 'selected':
            placement_history.append({
                'company': app.drive.company.company_name if app.drive and app.drive.company else '',
                'role': app.drive.job_role if app.drive else '',
                'year': app.applied_at.year if app.applied_at else '',
                'package': app.drive.package if app.drive else ''
            })

    data['placement_history'] = placement_history
    return jsonify({'student': data}), 200


@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # update user fields
    if 'name' in data:
        student.user.name = data['name']
    if 'email' in data:
        student.user.email = data['email'].lower().strip()

    # update student fields
    updatable_fields = ['department', 'year', 'cgpa', 'phone', 'address',
                        'marks_10th', 'marks_12th', 'backlogs', 'graduation_year', 'preferred_role']
    for field in updatable_fields:
        if field in data:
            setattr(student, field, data[field])

    if 'skills' in data:
        student.save_skills(data['skills'])

    db.session.commit()
    return jsonify({'message': 'Student updated', 'student': student.to_dict()}), 200


@admin_bp.route('/students/<int:student_id>/status', methods=['PUT'])
@admin_required
def change_student_status(student_id):
    student = Student.query.get_or_404(student_id)
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ('active', 'inactive'):
        return jsonify({'error': 'Status must be active or inactive'}), 400

    student.user.status = new_status
    db.session.commit()

    return jsonify({'message': 'Student status updated to ' + new_status}), 200


# ---- COMPANIES ----

@admin_bp.route('/companies', methods=['GET'])
@admin_required
def get_all_companies():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = Company.query.join(User)

    if search:
        search_term = '%' + search + '%'
        query = query.filter(
            db.or_(
                Company.company_name.ilike(search_term),
                Company.industry.ilike(search_term),
                Company.city.ilike(search_term)
            )
        )

    if status_filter and status_filter.lower() != 'all':
        if status_filter.lower() == 'blacklisted':
            query = query.filter(Company.blacklisted == True)
        else:
            query = query.filter(
                Company.approval_status == status_filter.lower(),
                Company.blacklisted == False
            )

    total = query.count()
    companies = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'companies': [c.to_dict() for c in companies],
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    }), 200


@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@admin_required
def get_company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify({'company': company.to_dict(show_drives=True)}), 200


@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'approved'
    company.blacklisted = False
    db.session.commit()
    return jsonify({'message': 'Company approved successfully'}), 200


@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@admin_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Company rejected'}), 200


@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    req_data = request.get_json() or {}
    company.blacklisted = req_data.get('blacklisted', True)
    db.session.commit()

    if company.blacklisted:
        return jsonify({'message': 'Company has been blacklisted'}), 200
    else:
        return jsonify({'message': 'Company removed from blacklist'}), 200


# ---- PLACEMENT DRIVES ----

@admin_bp.route('/drives', methods=['GET'])
@admin_required
def get_all_drives():
    status_filter = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = PlacementDrive.query.join(Company)

    if status_filter and status_filter.lower() != 'all':
        query = query.filter(PlacementDrive.status == status_filter.lower())

    total = query.count()
    drives = query.order_by(PlacementDrive.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'drives': [d.to_dict() for d in drives],
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    }), 200


@admin_bp.route('/drives/<int:drive_id>', methods=['GET'])
@admin_required
def get_drive_detail(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    return jsonify({'drive': drive.to_dict()}), 200


@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'open'
    db.session.commit()
    return jsonify({'message': 'Drive approved and is now open'}), 200


@admin_bp.route('/drives/<int:drive_id>/reject', methods=['PUT'])
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Drive rejected'}), 200


@admin_bp.route('/drives/<int:drive_id>/status', methods=['PUT'])
@admin_required
def update_drive_status(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    req_data = request.get_json()
    allowed = ['pending', 'open', 'closed', 'rejected']
    new_status = req_data.get('status', '').lower()

    if new_status not in allowed:
        return jsonify({'error': 'Status must be one of: ' + ', '.join(allowed)}), 400

    drive.status = new_status
    db.session.commit()
    return jsonify({'message': 'Drive status changed to ' + new_status}), 200


# ---- FILE SERVING ----

@admin_bp.route('/resumes/<filename>', methods=['GET'])
@admin_required
def download_resume(filename):
    from config import Config
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
