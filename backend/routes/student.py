from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import student_required
from models import db
from models.student import Student
from models.placement_drive import PlacementDrive
from models.application import Application
from services.file_service import save_resume, delete_resume

student_bp = Blueprint('student_routes', __name__, url_prefix='/api/student')

def get_student_by_user(user_id):
    # Query student via db session
    stud_obj = db.session.query(Student).filter(Student.user_id == int(user_id)).first()
    if stud_obj is None:
        return jsonify({'error': 'Student not found'}), 404
    return stud_obj

@student_bp.route('/stats', methods=['GET'])
@student_required
def get_student_stats():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):  # error response
        return stud

    # Count drives, applications, and scheduled interviews
    open_drives_count = db.session.query(PlacementDrive).filter(PlacementDrive.status == 'open').count()
    student_apps_count = db.session.query(Application).filter(Application.student_id == stud.id).count()
    
    interviews_count = db.session.query(Application).filter(
        Application.student_id == stud.id,
        Application.application_status == 'interview'
    ).count()

    # Compile array sequentially
    stats_data = []
    stats_data.append({'label': 'Available Drives', 'value': str(open_drives_count), 'icon': 'bi-briefcase', 'tone': 'primary'})
    stats_data.append({'label': 'Applied Drives', 'value': str(student_apps_count), 'icon': 'bi-send-check', 'tone': 'success'})
    stats_data.append({'label': 'Interview Schedule', 'value': str(interviews_count), 'icon': 'bi-calendar-event', 'tone': 'warning'})
    stats_data.append({'label': 'Placement Status', 'value': stud.placement_status, 'icon': 'bi-emoji-smile', 'tone': 'danger'})

    return jsonify({'stats': stats_data}), 200

@student_bp.route('/profile', methods=['GET'])
@student_required
def get_profile():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud
    return jsonify({'student': stud.to_dict()}), 200

@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud
        
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'No updates provided'}), 400

    # User table changes
    if 'name' in payload:
        stud.user.name = payload['name']
    if 'email' in payload:
        stud.user.email = payload['email'].lower().strip()

    # Student specific changes
    fields_list = ['department', 'year', 'cgpa', 'phone', 'address',
                   'marks_10th', 'marks_12th', 'backlogs', 'graduation_year', 'preferred_role']
                   
    for key in fields_list:
        if key in payload:
            setattr(stud, key, payload[key])

    if 'skills' in payload:
        stud.save_skills(payload['skills'])

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'student': stud.to_dict()}), 200

@student_bp.route('/resume', methods=['POST'])
@student_required
def upload_resume():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded. Use field name "resume"'}), 400

    file_obj = request.files['resume']
    previous_resume = stud.resume_path

    # Save resume
    saved_filename, error_msg = save_resume(file_obj, stud.id)
    if error_msg:
        return jsonify({'error': error_msg}), 400

    stud.resume_path = saved_filename
    db.session.commit()

    # Clean old files
    if previous_resume and previous_resume != saved_filename:
        delete_resume(previous_resume)

    return jsonify({
        'message': 'Resume uploaded successfully',
        'resume_path': saved_filename,
        'resume_url': f"/api/student/resume/{saved_filename}"
    }), 200

@student_bp.route('/resume/<filename>', methods=['GET'])
@student_required
def get_resume(filename):
    from flask import current_app
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@student_bp.route('/drives', methods=['GET'])
@student_required
def list_open_drives():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    search_query = request.args.get('search', '').strip()

    # Query matching drives
    query_builder = db.session.query(PlacementDrive).filter(PlacementDrive.status == 'open')

    if search_query:
        wildcard_term = f"%{search_query}%"
        query_builder = query_builder.filter(
            db.or_(
                PlacementDrive.job_role.ilike(wildcard_term),
                PlacementDrive.title.ilike(wildcard_term)
            )
        )

    all_drives = query_builder.order_by(PlacementDrive.created_at.desc()).all()

    # Retrieve applied drive IDs
    applied_records = db.session.query(Application).filter(Application.student_id == stud.id).all()
    applied_ids = set()
    for app in applied_records:
        applied_ids.add(app.drive_id)

    formatted_list = []
    for drive in all_drives:
        drive_dict = drive.to_dict()
        drive_dict['already_applied'] = drive.id in applied_ids
        formatted_list.append(drive_dict)

    return jsonify({'drives': formatted_list}), 200

@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@student_required
def get_drive_details(drive_id):
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    drive_record = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive_record:
        return jsonify({'error': 'Placement drive not found'}), 404
        
    drive_dict = drive_record.to_dict()

    # Check for existing application
    user_app = db.session.query(Application).filter(
        Application.student_id == stud.id,
        Application.drive_id == drive_id
    ).first()
    
    drive_dict['already_applied'] = user_app is not None

    if user_app is not None:
        drive_dict['application'] = user_app.to_dict(include_student=False)

    return jsonify({'drive': drive_dict}), 200

@student_bp.route('/applications', methods=['POST'])
@student_required
def apply_for_drive():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    payload = request.get_json()
    drive_id = payload.get('drive_id')

    if not drive_id:
        return jsonify({'error': 'drive_id is required'}), 400

    target_drive = db.session.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not target_drive:
        return jsonify({'error': 'Placement drive not found'}), 404

    if target_drive.status != 'open':
        return jsonify({'error': 'This drive is not accepting applications right now'}), 400

    # Verify duplicate application
    duplicate_app = db.session.query(Application).filter(
        Application.student_id == stud.id,
        Application.drive_id == drive_id
    ).first()
    
    if duplicate_app is not None:
        return jsonify({'error': 'You already applied for this drive'}), 409

    # Insert application record
    new_application = Application(
        student_id=stud.id,
        drive_id=drive_id,
        cover_note=payload.get('cover_note'),
        application_status='applied'
    )
    db.session.add(new_application)

    # Change placement state
    if stud.placement_status == 'Not Placed':
        stud.placement_status = 'Applied'

    db.session.commit()

    return jsonify({
        'message': 'Application submitted successfully',
        'application': new_application.to_dict()
    }), 201

@student_bp.route('/applications', methods=['GET'])
@student_required
def get_my_applications():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    user_applications = db.session.query(Application).filter(
        Application.student_id == stud.id
    ).order_by(Application.applied_at.desc()).all()

    formatted_apps = []
    for app in user_applications:
        formatted_apps.append(app.to_dict(include_student=False))

    return jsonify({'applications': formatted_apps}), 200

@student_bp.route('/interviews', methods=['GET'])
@student_required
def get_my_interviews():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    # Retrieve all interview application records
    interview_apps = db.session.query(Application).filter(
        Application.student_id == stud.id,
        Application.application_status == 'interview'
    ).all()

    interview_details = []
    for app in interview_apps:
        if app.interview:
            detail = app.interview.to_dict()
            detail['drive_title'] = app.drive.title if app.drive else ''
            detail['company_name'] = app.drive.company.company_name if app.drive and app.drive.company else ''
            interview_details.append(detail)

    return jsonify({'interviews': interview_details}), 200

@student_bp.route('/history', methods=['GET'])
@student_required
def get_placement_history():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    if isinstance(stud, tuple):
        return stud

    # Retrieve selected applications
    selections = db.session.query(Application).filter(
        Application.student_id == stud.id,
        Application.application_status == 'selected'
    ).all()

    selection_history = []
    for app in selections:
        selection_history.append({
            'company': app.drive.company.company_name if app.drive and app.drive.company else '',
            'role': app.drive.job_role if app.drive else '',
            'year': app.applied_at.year if app.applied_at else '',
            'package': app.drive.package if app.drive else '',
            'drive_title': app.drive.title if app.drive else ''
        })

    return jsonify({'history': selection_history}), 200

