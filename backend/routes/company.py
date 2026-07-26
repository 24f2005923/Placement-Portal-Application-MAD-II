from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import company_required
from models import db
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.interview import Interview
from models.result import Result
from models.student import Student
from cache import cache
from cache.decorators import cache_response

company_bp = Blueprint('company_routes', __name__, url_prefix='/api/company')

def find_company_by_uid(uid):
    company_obj = db.session.query(Company).filter(Company.user_id == int(uid)).first()
    if company_obj is None:
        return jsonify({'error': 'Company not found'}), 404
    return company_obj

@company_bp.route('/stats', methods=['GET'])
@company_required
@cache_response(lambda: f"company:stats:{get_jwt_identity()}", ttl=120)
def get_company_stats():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    # Gather drive ids
    drive_id_list = []
    for d in comp.drives:
        drive_id_list.append(d.id)
        
    total_drives = len(drive_id_list)

    if total_drives > 0:
        total_applications = db.session.query(Application).filter(
            Application.drive_id.in_(drive_id_list)
        ).count()
        
        shortlisted = db.session.query(Application).filter(
            Application.drive_id.in_(drive_id_list),
            Application.application_status.in_(['shortlisted', 'interview', 'selected'])
        ).count()
        
        selected = db.session.query(Application).filter(
            Application.drive_id.in_(drive_id_list),
            Application.application_status == 'selected'
        ).count()
    else:
        total_applications = 0
        shortlisted = 0
        selected = 0

    stats_list = []
    stats_list.append({'label': 'Total Drives', 'value': str(total_drives), 'icon': 'bi-megaphone', 'tone': 'primary'})
    stats_list.append({'label': 'Applications Received', 'value': str(total_applications), 'icon': 'bi-inbox', 'tone': 'success'})
    stats_list.append({'label': 'Shortlisted Students', 'value': str(shortlisted), 'icon': 'bi-person-check', 'tone': 'warning'})
    stats_list.append({'label': 'Selected Students', 'value': str(selected), 'icon': 'bi-trophy', 'tone': 'danger'})

    return jsonify({'stats': stats_list}), 200

@company_bp.route('/profile', methods=['GET'])
@company_required
@cache_response(lambda: f"company:profile:{get_jwt_identity()}", ttl=300)
def get_company_profile():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
    return jsonify({'company': comp.to_dict()}), 200

@company_bp.route('/profile', methods=['PUT'])
@company_required
def update_company_profile():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'No data provided'}), 400

    # Fields list
    allowed_fields = ['company_name', 'industry', 'website', 'description',
                      'contact_person', 'contact_email', 'contact_phone', 'city', 'address']
                      
    for field in allowed_fields:
        if field in payload:
            setattr(comp, field, payload[field])

    if 'name' in payload:
        comp.user.name = payload['name']

    db.session.commit()

    # Invalidate this company's cached profile and stats
    cache.delete(f'company:profile:{uid}')
    cache.delete(f'company:stats:{uid}')

    return jsonify({'message': 'Profile updated', 'company': comp.to_dict()}), 200

@company_bp.route('/drives', methods=['GET'])
@company_required
@cache_response(lambda: f"company:drives:{get_jwt_identity()}", ttl=120)
def get_company_drives():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    # Query drives sequentially
    drives = db.session.query(PlacementDrive).filter(
        PlacementDrive.company_id == comp.id
    ).order_by(PlacementDrive.created_at.desc()).all()

    formatted_drives = []
    for d in drives:
        formatted_drives.append(d.to_dict())

    return jsonify({'drives': formatted_drives}), 200

@company_bp.route('/drives', methods=['POST'])
@company_required
def create_new_drive():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    if comp.approval_status != 'approved':
        return jsonify({'error': 'Your company must be approved by admin before creating drives'}), 403

    payload = request.get_json()
    if not payload or not payload.get('job_role'):
        return jsonify({'error': 'job_role is required'}), 400

    deadline_val = None
    if payload.get('deadline'):
        try:
            deadline_val = date.fromisoformat(payload['deadline'])
        except ValueError:
            return jsonify({'error': 'Deadline date format should be YYYY-MM-DD'}), 400

    created_drive = PlacementDrive(
        company_id=comp.id,
        title=payload.get('title', payload['job_role']),
        job_role=payload['job_role'],
        package=payload.get('package'),
        eligibility=payload.get('eligibility'),
        openings=payload.get('openings', 1),
        deadline=deadline_val,
        description=payload.get('description'),
        status='pending'
    )

    db.session.add(created_drive)
    db.session.commit()

    # Invalidate company drive list and admin drive caches
    cache.delete(f'company:drives:{uid}')
    cache.delete(f'company:stats:{uid}')
    cache.delete_pattern('admin:drives:*')
    cache.delete('admin:activities')

    return jsonify({'message': 'Drive submitted for admin approval', 'drive': created_drive.to_dict()}), 201

@company_bp.route('/drives/<int:drive_id>', methods=['GET'])
@company_required
def get_single_drive(drive_id):
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    drive_record = db.session.query(PlacementDrive).filter(
        PlacementDrive.id == drive_id,
        PlacementDrive.company_id == comp.id
    ).first()
    
    if drive_record is None:
        return jsonify({'error': 'Placement drive not found'}), 404
        
    return jsonify({'drive': drive_record.to_dict()}), 200

@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@company_required
def update_drive(drive_id):
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    drive_record = db.session.query(PlacementDrive).filter(
        PlacementDrive.id == drive_id,
        PlacementDrive.company_id == comp.id
    ).first()
    
    if drive_record is None:
        return jsonify({'error': 'Placement drive not found'}), 404
        
    payload = request.get_json()

    updatable = ['title', 'job_role', 'package', 'eligibility', 'openings', 'description']
    for field in updatable:
        if field in payload:
            setattr(drive_record, field, payload[field])

    if 'deadline' in payload and payload['deadline']:
        try:
            drive_record.deadline = date.fromisoformat(payload['deadline'])
        except ValueError:
            return jsonify({'error': 'Deadline format should be YYYY-MM-DD'}), 400

    if 'status' in payload and payload['status'] in ('pending', 'open', 'closed'):
        drive_record.status = payload['status']

    db.session.commit()

    cache.delete(f'company:drives:{uid}')
    cache.delete_pattern('admin:drives:*')

    return jsonify({'message': 'Drive updated', 'drive': drive_record.to_dict()}), 200

@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@company_required
def delete_drive(drive_id):
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    drive_record = db.session.query(PlacementDrive).filter(
        PlacementDrive.id == drive_id,
        PlacementDrive.company_id == comp.id
    ).first()
    
    if drive_record is None:
        return jsonify({'error': 'Placement drive not found'}), 404
        
    db.session.delete(drive_record)
    db.session.commit()

    cache.delete(f'company:drives:{uid}')
    cache.delete(f'company:stats:{uid}')
    cache.delete_pattern('admin:drives:*')
    cache.delete('admin:stats')

    return jsonify({'message': 'Drive deleted'}), 200

@company_bp.route('/applications', methods=['GET'])
@company_required
def get_received_applications():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp

    drive_id_list = []
    for d in comp.drives:
        drive_id_list.append(d.id)

    status_filter = request.args.get('status', '').strip()
    drive_filter = request.args.get('drive_id', '').strip()

    query_builder = db.session.query(Application).filter(Application.drive_id.in_(drive_id_list))

    if status_filter:
        query_builder = query_builder.filter(Application.application_status == status_filter.lower())

    if drive_filter:
        query_builder = query_builder.filter(Application.drive_id == int(drive_filter))

    applications_list = query_builder.order_by(Application.applied_at.desc()).all()
    
    formatted_apps = []
    for a in applications_list:
        formatted_apps.append(a.to_dict())
        
    return jsonify({'applications': formatted_apps}), 200

@company_bp.route('/applications/<int:app_id>/shortlist', methods=['PUT'])
@company_required
def shortlist_student(app_id):
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    app_record = db.session.query(Application).filter(Application.id == app_id).first()
    if app_record is None:
        return jsonify({'error': 'Application not found'}), 404

    drive_ids = []
    for d in comp.drives:
        drive_ids.append(d.id)
        
    if app_record.drive_id not in drive_ids:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    app_record.application_status = 'shortlisted'

    # Update candidate status
    target_student = app_record.student
    if target_student is not None:
        if target_student.placement_status not in ('Placed', 'Interview'):
            target_student.placement_status = 'Applied'

    db.session.commit()

    # Invalidate company stats (shortlisted count changed)
    cache.delete(f'company:stats:{uid}')

    return jsonify({'message': 'Student shortlisted', 'application': app_record.to_dict()}), 200

@company_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@company_required
def reject_application(app_id):
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    app_record = db.session.query(Application).filter(Application.id == app_id).first()
    if app_record is None:
        return jsonify({'error': 'Application not found'}), 404

    drive_ids = []
    for d in comp.drives:
        drive_ids.append(d.id)
        
    if app_record.drive_id not in drive_ids:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    app_record.application_status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Application rejected'}), 200

@company_bp.route('/interviews', methods=['GET'])
@company_required
def get_scheduled_interviews():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    drive_ids = []
    for d in comp.drives:
        drive_ids.append(d.id)

    matched_applications = db.session.query(Application).filter(
        Application.drive_id.in_(drive_ids)
    ).all()

    interview_details = []
    for app in matched_applications:
        if app.interview:
            interview_dict = app.interview.to_dict()
            interview_dict['student_name'] = app.student.user.name if app.student and app.student.user else ''
            interview_dict['drive_title'] = app.drive.title if app.drive else ''
            interview_details.append(interview_dict)

    return jsonify({'interviews': interview_details}), 200

@company_bp.route('/interviews', methods=['POST'])
@company_required
def schedule_interview():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    payload = request.get_json()

    app_id = payload.get('application_id')
    if not app_id:
        return jsonify({'error': 'application_id is required'}), 400

    app_record = db.session.query(Application).filter(Application.id == app_id).first()
    if app_record is None:
        return jsonify({'error': 'Application not found'}), 404

    drive_ids = []
    for d in comp.drives:
        drive_ids.append(d.id)
        
    if app_record.drive_id not in drive_ids:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    # Resolve interview row
    if app_record.interview:
        interview_row = app_record.interview
    else:
        interview_row = Interview(application_id=app_id)
        db.session.add(interview_row)

    if payload.get('interview_date'):
        try:
            interview_row.interview_date = date.fromisoformat(payload['interview_date'])
        except ValueError:
            return jsonify({'error': 'Interview date format should be YYYY-MM-DD'}), 400

    interview_row.interview_time = payload.get('interview_time')
    interview_row.interview_mode = payload.get('interview_mode', 'online')
    interview_row.interview_link = payload.get('interview_link')
    interview_row.round_name = payload.get('round_name')
    interview_row.remarks = payload.get('remarks')

    app_record.application_status = 'interview'
    if app_record.student:
        app_record.student.placement_status = 'Interview'

    db.session.commit()

    # Invalidate stats (interview count changed)
    cache.delete(f'company:stats:{uid}')
    if app_record.student:
        student_user_id = app_record.student.user_id
        cache.delete(f'student:stats:{student_user_id}')

    return jsonify({'message': 'Interview scheduled successfully', 'interview': interview_row.to_dict()}), 201

@company_bp.route('/results', methods=['GET'])
@company_required
def get_result_candidates():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    drive_ids = []
    for d in comp.drives:
        drive_ids.append(d.id)

    applications_in_stage = db.session.query(Application).filter(
        Application.drive_id.in_(drive_ids),
        Application.application_status.in_(['interview', 'shortlisted'])
    ).all()

    candidates_list = []
    for app in applications_in_stage:
        candidates_list.append({
            'application_id': app.id,
            'student_name': app.student.user.name if app.student and app.student.user else '',
            'drive_title': app.drive.title if app.drive else '',
            'drive_role': app.drive.job_role if app.drive else '',
            'application_status': app.application_status,
            'result': app.result.to_dict() if app.result else None
        })

    return jsonify({'candidates': candidates_list}), 200

@company_bp.route('/results/publish', methods=['POST'])
@company_required
def publish_result():
    uid = get_jwt_identity()
    comp = find_company_by_uid(uid)
    if isinstance(comp, tuple):
        return comp
        
    payload = request.get_json()

    app_id = payload.get('application_id')
    status_result = payload.get('result_status')

    if not app_id:
        return jsonify({'error': 'application_id is required'}), 400

    if status_result not in ('selected', 'rejected'):
        return jsonify({'error': 'result_status must be selected or rejected'}), 400

    app_record = db.session.query(Application).filter(Application.id == app_id).first()
    if app_record is None:
        return jsonify({'error': 'Application not found'}), 404

    drive_ids = []
    for d in comp.drives:
        drive_ids.append(d.id)
        
    if app_record.drive_id not in drive_ids:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    # Check for result record
    if app_record.result:
        app_record.result.result_status = status_result
        app_record.result.remarks = payload.get('remarks')
    else:
        new_res = Result(
            application_id=app_id,
            result_status=status_result,
            remarks=payload.get('remarks')
        )
        db.session.add(new_res)

    app_record.application_status = status_result

    if status_result == 'selected' and app_record.student:
        app_record.student.placement_status = 'Placed'

    db.session.commit()

    # Invalidate stats caches (placement counts changed)
    cache.delete(f'company:stats:{uid}')
    cache.delete('admin:stats')
    cache.delete('admin:report_stats')
    if app_record.student:
        student_user_id = app_record.student.user_id
        cache.delete(f'student:stats:{student_user_id}')

    return jsonify({'message': f"Result published: {status_result}"}), 200
