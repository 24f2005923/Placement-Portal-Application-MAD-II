from flask import Blueprint, request, jsonify, send_from_directory
from middleware.auth_middleware import admin_required
from models import db
from models.user import User
from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.result import Result
from cache import cache
from cache.decorators import cache_response

admin_bp = Blueprint('admin_routes', __name__, url_prefix='/api/admin')


# ── Helper ────────────────────────────────────────────────────────

def get_percentage(part, total):
    return round((part / total) * 100, 1) if total > 0 else 0.0


# ── Dashboard & Stats ─────────────────────────────────────────────

@admin_bp.route('/stats', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:stats', ttl=300)   # cache 5 min
def get_dashboard_stats():
    student_total_count = db.session.query(Student).count()
    active_company_count = db.session.query(Company).filter(Company.blacklisted == False).count()

    approved_open_drives = db.session.query(PlacementDrive).filter(
        PlacementDrive.status.in_(['open', 'approved'])
    ).count()

    placed_students_count = db.session.query(Student).filter(Student.placement_status == 'Placed').count()

    stats_list = []
    stats_list.append({'label': 'Total Students', 'value': str(student_total_count), 'icon': 'bi-people', 'tone': 'primary'})
    stats_list.append({'label': 'Total Companies', 'value': str(active_company_count), 'icon': 'bi-buildings', 'tone': 'success'})
    stats_list.append({'label': 'Active Drives', 'value': str(approved_open_drives), 'icon': 'bi-megaphone', 'tone': 'warning'})
    stats_list.append({'label': 'Placed Students', 'value': str(placed_students_count), 'icon': 'bi-award', 'tone': 'danger'})

    return jsonify({'stats': stats_list}), 200

@admin_bp.route('/activities', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:activities', ttl=120)   # cache 2 min — changes frequently
def get_recent_activities():
    activities_log = []

    # Get last 3 applications
    latest_applications = db.session.query(Application).order_by(Application.applied_at.desc()).limit(3).all()
    for app in latest_applications:
        cand_name = ''
        if app.student and app.student.user:
            cand_name = app.student.user.name
        drive_name = app.drive.title if app.drive else 'Unknown'
        
        date_str = app.applied_at.strftime('%Y-%m-%d %H:%M') if app.applied_at else ''
        activities_log.append({
            'title': f"{cand_name} applied for {drive_name}",
            'meta': date_str,
            'tone': 'primary'
        })

    # Show pending company approvals
    pending_companies_count = db.session.query(Company).filter(Company.approval_status == 'pending').count()
    if pending_companies_count > 0:
        activities_log.append({
            'title': f"{pending_companies_count} company registration(s) need approval",
            'meta': 'Pending',
            'tone': 'danger'
        })

    # Show pending drive approvals
    pending_drives_count = db.session.query(PlacementDrive).filter(PlacementDrive.status == 'pending').count()
    if pending_drives_count > 0:
        activities_log.append({
            'title': f"{pending_drives_count} placement drive(s) waiting for approval",
            'meta': 'Pending',
            'tone': 'warning'
        })

    return jsonify({'activities': activities_log}), 200


@admin_bp.route('/reports/stats', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:report_stats', ttl=600)   # cache 10 min — reports change rarely
def get_report_stats():
    student_total_count = db.session.query(Student).count()
    placed_students_count = db.session.query(Student).filter(Student.placement_status == 'Placed').count()
    placement_rate = get_percentage(placed_students_count, student_total_count)

    drives_total_count = db.session.query(PlacementDrive).count()
    approved_drives_count = db.session.query(PlacementDrive).filter(
        PlacementDrive.status.in_(['open', 'approved', 'closed'])
    ).count()
    drive_conversion = get_percentage(approved_drives_count, drives_total_count)

    total_applications = db.session.query(Application).count()
    selected_applications = db.session.query(Application).filter(Application.application_status == 'selected').count()
    interview_success = get_percentage(selected_applications, total_applications)

    report_metrics = []
    report_metrics.append({'label': 'Placement Rate', 'value': f"{placement_rate}%", 'icon': 'bi-graph-up', 'tone': 'primary'})
    report_metrics.append({'label': 'Drive Conversion', 'value': f"{drive_conversion}%", 'icon': 'bi-arrow-repeat', 'tone': 'success'})
    report_metrics.append({'label': 'Average Package', 'value': 'N/A', 'icon': 'bi-currency-rupee', 'tone': 'warning'})
    report_metrics.append({'label': 'Interview Success', 'value': f"{interview_success}%", 'icon': 'bi-person-check', 'tone': 'danger'})

    return jsonify({'stats': report_metrics}), 200


# ── Settings ──────────────────────────────────────────────────────

# Global portal configuration dict
system_settings = {
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
    return jsonify({'settings': system_settings}), 200

@admin_bp.route('/settings', methods=['PUT'])
@admin_required
def update_settings():
    payload = request.get_json()
    if payload:
        system_settings.update(payload)
    return jsonify({'message': 'Settings updated', 'settings': system_settings}), 200


# ── Students ──────────────────────────────────────────────────────

@admin_bp.route('/students', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:students:{request.args.get('search','').strip()}:{request.args.get('status','')}:{request.args.get('page',1)}",
    ttl=180   # cache 3 min
)
def get_all_students():
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))

    query_builder = db.session.query(Student).join(User)

    if search_term:
        wildcard_term = f"%{search_term}%"
        query_builder = query_builder.filter(
            db.or_(
                User.name.ilike(wildcard_term),
                Student.register_number.ilike(wildcard_term),
                Student.department.ilike(wildcard_term)
            )
        )

    if status_filter and status_filter.lower() != 'all':
        if status_filter.lower() == 'inactive':
            query_builder = query_builder.filter(User.status == 'inactive')
        else:
            query_builder = query_builder.filter(Student.placement_status.ilike(status_filter))

    total_records = query_builder.count()
    
    offset_val = (page_num - 1) * records_per_page
    students_list = query_builder.offset(offset_val).limit(records_per_page).all()

    serialized_students = []
    for s in students_list:
        serialized_students.append(s.to_dict())

    return jsonify({
        'students': serialized_students,
        'total': total_records,
        'page': page_num,
        'pages': (total_records + records_per_page - 1) // records_per_page
    }), 200

@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:student:{request.view_args.get('student_id')}", ttl=180)
def get_student_detail(student_id):
    student_record = db.session.query(Student).filter(Student.id == student_id).first()
    if student_record is None:
        return jsonify({'error': 'Student not found'}), 404
        
    student_dict = student_record.to_dict()

    # Load placement history
    placement_history_list = []
    for app in student_record.applications:
        if app.result and app.result.result_status == 'selected':
            placement_history_list.append({
                'company': app.drive.company.company_name if app.drive and app.drive.company else '',
                'role': app.drive.job_role if app.drive else '',
                'year': app.applied_at.year if app.applied_at else '',
                'package': app.drive.package if app.drive else ''
            })

    student_dict['placement_history'] = placement_history_list
    return jsonify({'student': student_dict}), 200

@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    student_record = db.session.query(Student).filter(Student.id == student_id).first()
    if student_record is None:
        return jsonify({'error': 'Student not found'}), 404
        
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'No data provided'}), 400

    if 'name' in payload:
        student_record.user.name = payload['name']
    if 'email' in payload:
        student_record.user.email = payload['email'].lower().strip()

    updatable_fields = ['department', 'year', 'cgpa', 'phone', 'address',
                        'marks_10th', 'marks_12th', 'backlogs', 'graduation_year', 'preferred_role']
                        
    for field in updatable_fields:
        if field in payload:
            setattr(student_record, field, payload[field])

    if 'skills' in payload:
        student_record.save_skills(payload['skills'])

    db.session.commit()

    # Invalidate all student-related caches so next read reflects new data
    cache.delete_pattern('admin:students:*')
    cache.delete(f'admin:student:{student_id}')
    cache.delete('admin:stats')

    return jsonify({'message': 'Student updated', 'student': student_record.to_dict()}), 200

@admin_bp.route('/students/<int:student_id>/status', methods=['PUT'])
@admin_required
def change_student_status(student_id):
    student_record = db.session.query(Student).filter(Student.id == student_id).first()
    if student_record is None:
        return jsonify({'error': 'Student not found'}), 404
        
    payload = request.get_json()
    new_status = payload.get('status')

    if new_status not in ('active', 'inactive'):
        return jsonify({'error': 'Status must be active or inactive'}), 400

    student_record.user.status = new_status
    db.session.commit()

    # Invalidate student caches
    cache.delete_pattern('admin:students:*')
    cache.delete(f'admin:student:{student_id}')

    return jsonify({'message': f"Student status updated to {new_status}"}), 200


# ── Companies ─────────────────────────────────────────────────────

@admin_bp.route('/companies', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:companies:{request.args.get('search','').strip()}:{request.args.get('status','')}:{request.args.get('page',1)}",
    ttl=180
)
def get_all_companies():
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))

    query_builder = db.session.query(Company).join(User)

    if search_term:
        wildcard_term = f"%{search_term}%"
        query_builder = query_builder.filter(
            db.or_(
                Company.company_name.ilike(wildcard_term),
                Company.industry.ilike(wildcard_term),
                Company.city.ilike(wildcard_term)
            )
        )

    if status_filter and status_filter.lower() != 'all':
        if status_filter.lower() == 'blacklisted':
            query_builder = query_builder.filter(Company.blacklisted == True)
        else:
            query_builder = query_builder.filter(
                Company.approval_status == status_filter.lower(),
                Company.blacklisted == False
            )

    total_records = query_builder.count()
    
    offset_val = (page_num - 1) * records_per_page
    companies_list = query_builder.offset(offset_val).limit(records_per_page).all()

    serialized_companies = []
    for c in companies_list:
        serialized_companies.append(c.to_dict())

    return jsonify({
        'companies': serialized_companies,
        'total': total_records,
        'page': page_num,
        'pages': (total_records + records_per_page - 1) // records_per_page
    }), 200

@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:company:{request.view_args.get('company_id')}", ttl=180)
def get_company_detail(company_id):
    company_record = db.session.query(Company).filter(Company.id == company_id).first()
    if company_record is None:
        return jsonify({'error': 'Company not found'}), 404
        
    return jsonify({'company': company_record.to_dict(show_drives=True)}), 200

@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@admin_required
def approve_company(company_id):
    company_record = db.session.query(Company).filter(Company.id == company_id).first()
    if company_record is None:
        return jsonify({'error': 'Company not found'}), 404
        
    company_record.approval_status = 'approved'
    company_record.blacklisted = False
    db.session.commit()

    cache.delete_pattern('admin:companies:*')
    cache.delete(f'admin:company:{company_id}')
    cache.delete('admin:stats')

    return jsonify({'message': 'Company approved successfully'}), 200

@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@admin_required
def reject_company(company_id):
    company_record = db.session.query(Company).filter(Company.id == company_id).first()
    if company_record is None:
        return jsonify({'error': 'Company not found'}), 404
        
    company_record.approval_status = 'rejected'
    db.session.commit()

    cache.delete_pattern('admin:companies:*')
    cache.delete(f'admin:company:{company_id}')

    return jsonify({'message': 'Company rejected'}), 200

@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_company(company_id):
    company_record = db.session.query(Company).filter(Company.id == company_id).first()
    if company_record is None:
        return jsonify({'error': 'Company not found'}), 404
        
    payload = request.get_json() or {}
    company_record.blacklisted = payload.get('blacklisted', True)
    db.session.commit()

    cache.delete_pattern('admin:companies:*')
    cache.delete(f'admin:company:{company_id}')
    cache.delete('admin:stats')

    if company_record.blacklisted:
        return jsonify({'message': 'Company has been blacklisted'}), 200
    else:
        return jsonify({'message': 'Company removed from blacklist'}), 200


# ── Placement Drives ──────────────────────────────────────────────

@admin_bp.route('/drives', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:drives:{request.args.get('status','')}:{request.args.get('page',1)}",
    ttl=180
)
def get_all_drives():
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))

    query_builder = db.session.query(PlacementDrive).join(Company)

    if status_filter and status_filter.lower() != 'all':
        query_builder = query_builder.filter(PlacementDrive.status == status_filter.lower())

    total_records = query_builder.count()
    
    offset_val = (page_num - 1) * records_per_page
    drives_list = query_builder.order_by(PlacementDrive.created_at.desc()).offset(offset_val).limit(records_per_page).all()

    serialized_drives = []
    for d in drives_list:
        serialized_drives.append(d.to_dict())

    return jsonify({
        'drives': serialized_drives,
        'total': total_records,
        'page': page_num,
        'pages': (total_records + records_per_page - 1) // records_per_page
    }), 200

@admin_bp.route('/drives/<int:drive_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:drive:{request.view_args.get('drive_id')}", ttl=180)
def get_drive_detail(drive_id):
    drive_record = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if drive_record is None:
        return jsonify({'error': 'Drive not found'}), 404
        
    return jsonify({'drive': drive_record.to_dict()}), 200

@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@admin_required
def approve_drive(drive_id):
    drive_record = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if drive_record is None:
        return jsonify({'error': 'Drive not found'}), 404
        
    drive_record.status = 'open'
    db.session.commit()

    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')
    cache.delete('admin:stats')
    cache.delete('admin:activities')

    return jsonify({'message': 'Drive approved and is now open'}), 200

@admin_bp.route('/drives/<int:drive_id>/reject', methods=['PUT'])
@admin_required
def reject_drive(drive_id):
    drive_record = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if drive_record is None:
        return jsonify({'error': 'Drive not found'}), 404
        
    drive_record.status = 'rejected'
    db.session.commit()

    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')

    return jsonify({'message': 'Drive rejected'}), 200

@admin_bp.route('/drives/<int:drive_id>/status', methods=['PUT'])
@admin_required
def update_drive_status(drive_id):
    drive_record = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if drive_record is None:
        return jsonify({'error': 'Drive not found'}), 404
        
    payload = request.get_json()
    allowed = ['pending', 'open', 'closed', 'rejected']
    new_status = payload.get('status', '').lower()

    if new_status not in allowed:
        allowed_str = ', '.join(allowed)
        return jsonify({'error': f"Status must be one of: {allowed_str}"}), 400

    drive_record.status = new_status
    db.session.commit()

    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')
    cache.delete('admin:stats')

    return jsonify({'message': f"Drive status changed to {new_status}"}), 200

@admin_bp.route('/resumes/<filename>', methods=['GET'])
@admin_required
def download_resume(filename):
    from config import Config
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
