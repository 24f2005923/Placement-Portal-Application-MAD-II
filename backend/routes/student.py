from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import student_required
from models import db
from models.student import Student
from models.placement_drive import PlacementDrive
from models.application import Application
from services.file_service import save_resume, delete_resume

# all student routes go under /api/student
student_bp = Blueprint('student', __name__, url_prefix='/api/student')


# helper to get student by user id from jwt token
def get_student_by_user(user_id):
    stud = Student.query.filter_by(user_id=int(user_id)).first_or_404()
    return stud


# ---- DASHBOARD ----

@student_bp.route('/stats', methods=['GET'])
@student_required
def get_student_stats():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    # count available drives
    available = PlacementDrive.query.filter_by(status='open').count()

    # count applications by this student
    applied = Application.query.filter_by(student_id=stud.id).count()

    # count interview calls
    interviews = Application.query.filter_by(
        student_id=stud.id,
        application_status='interview'
    ).count()

    return jsonify({
        'stats': [
            {'label': 'Available Drives', 'value': str(available), 'icon': 'bi-briefcase', 'tone': 'primary'},
            {'label': 'Applied Drives', 'value': str(applied), 'icon': 'bi-send-check', 'tone': 'success'},
            {'label': 'Interview Schedule', 'value': str(interviews), 'icon': 'bi-calendar-event', 'tone': 'warning'},
            {'label': 'Placement Status', 'value': stud.placement_status, 'icon': 'bi-emoji-smile', 'tone': 'danger'}
        ]
    }), 200


# ---- PROFILE ----

@student_bp.route('/profile', methods=['GET'])
@student_required
def get_profile():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    return jsonify({'student': stud.to_dict()}), 200


@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # update name and email in user table
    if 'name' in data:
        stud.user.name = data['name']
    if 'email' in data:
        stud.user.email = data['email'].lower().strip()

    # update student profile fields
    fields_to_update = ['department', 'year', 'cgpa', 'phone', 'address',
                        'marks_10th', 'marks_12th', 'backlogs', 'graduation_year', 'preferred_role']
    for field in fields_to_update:
        if field in data:
            setattr(stud, field, data[field])

    if 'skills' in data:
        stud.save_skills(data['skills'])

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully', 'student': stud.to_dict()}), 200


# ---- RESUME ----

@student_bp.route('/resume', methods=['POST'])
@student_required
def upload_resume():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded. Use field name "resume"'}), 400

    uploaded_file = request.files['resume']
    old_resume = stud.resume_path

    # save the file using the file service
    saved_name, error_msg = save_resume(uploaded_file, stud.id)

    if error_msg:
        return jsonify({'error': error_msg}), 400

    # update resume path in database
    stud.resume_path = saved_name
    db.session.commit()

    # remove old resume file if it existed
    if old_resume and old_resume != saved_name:
        delete_resume(old_resume)

    return jsonify({
        'message': 'Resume uploaded successfully',
        'resume_path': saved_name,
        'resume_url': '/api/student/resume/' + saved_name
    }), 200


@student_bp.route('/resume/<filename>', methods=['GET'])
@student_required
def get_resume(filename):
    from flask import current_app
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# ---- PLACEMENT DRIVES ----

@student_bp.route('/drives', methods=['GET'])
@student_required
def list_open_drives():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    search = request.args.get('search', '').strip()

    # only show open drives
    query = PlacementDrive.query.filter_by(status='open')

    if search:
        search_term = '%' + search + '%'
        query = query.filter(
            db.or_(
                PlacementDrive.job_role.ilike(search_term),
                PlacementDrive.title.ilike(search_term)
            )
        )

    all_drives = query.order_by(PlacementDrive.created_at.desc()).all()

    # get the drive ids this student already applied to
    student_apps = Application.query.filter_by(student_id=stud.id).all()
    applied_ids = set()
    for app in student_apps:
        applied_ids.add(app.drive_id)

    result = []
    for drive in all_drives:
        d = drive.to_dict()
        d['already_applied'] = drive.id in applied_ids
        result.append(d)

    return jsonify({'drives': result}), 200


@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@student_required
def get_drive_details(drive_id):
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive_data = drive.to_dict()

    # check if student already applied
    existing_app = Application.query.filter_by(student_id=stud.id, drive_id=drive_id).first()
    drive_data['already_applied'] = existing_app is not None

    if existing_app:
        drive_data['application'] = existing_app.to_dict(include_student=False)

    return jsonify({'drive': drive_data}), 200


# ---- APPLICATIONS ----

@student_bp.route('/applications', methods=['POST'])
@student_required
def apply_for_drive():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    req_data = request.get_json()
    drive_id = req_data.get('drive_id')

    if not drive_id:
        return jsonify({'error': 'drive_id is required'}), 400

    # check drive exists and is open
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != 'open':
        return jsonify({'error': 'This drive is not accepting applications right now'}), 400

    # check if already applied
    already_applied = Application.query.filter_by(student_id=stud.id, drive_id=drive_id).first()
    if already_applied:
        return jsonify({'error': 'You already applied for this drive'}), 409

    # create new application
    new_app = Application(
        student_id=stud.id,
        drive_id=drive_id,
        cover_note=req_data.get('cover_note'),
        application_status='applied'
    )
    db.session.add(new_app)

    # update student placement status if not placed
    if stud.placement_status == 'Not Placed':
        stud.placement_status = 'Applied'

    db.session.commit()

    return jsonify({
        'message': 'Application submitted successfully',
        'application': new_app.to_dict()
    }), 201


@student_bp.route('/applications', methods=['GET'])
@student_required
def get_my_applications():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    apps = Application.query.filter_by(student_id=stud.id).order_by(
        Application.applied_at.desc()
    ).all()

    return jsonify({'applications': [a.to_dict(include_student=False) for a in apps]}), 200


# ---- INTERVIEWS ----

@student_bp.route('/interviews', methods=['GET'])
@student_required
def get_my_interviews():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    # get applications with interview status
    interview_apps = Application.query.filter_by(
        student_id=stud.id,
        application_status='interview'
    ).all()

    interview_list = []
    for app in interview_apps:
        if app.interview:
            interview_data = app.interview.to_dict()
            interview_data['drive_title'] = app.drive.title if app.drive else ''
            interview_data['company_name'] = app.drive.company.company_name if app.drive and app.drive.company else ''
            interview_list.append(interview_data)

    return jsonify({'interviews': interview_list}), 200


# ---- PLACEMENT HISTORY ----

@student_bp.route('/history', methods=['GET'])
@student_required
def get_placement_history():
    uid = get_jwt_identity()
    stud = get_student_by_user(uid)

    # get all selected applications
    selected = Application.query.filter_by(
        student_id=stud.id,
        application_status='selected'
    ).all()

    history = []
    for app in selected:
        history.append({
            'company': app.drive.company.company_name if app.drive and app.drive.company else '',
            'role': app.drive.job_role if app.drive else '',
            'year': app.applied_at.year if app.applied_at else '',
            'package': app.drive.package if app.drive else '',
            'drive_title': app.drive.title if app.drive else ''
        })

    return jsonify({'history': history}), 200
