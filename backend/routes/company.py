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

# all company routes go under /api/company
company_bp = Blueprint('company', __name__, url_prefix='/api/company')


# helper function to get company by user id from jwt
def get_company_by_user(user_id):
    comp = Company.query.filter_by(user_id=int(user_id)).first_or_404()
    return comp


# ---- DASHBOARD ----

@company_bp.route('/stats', methods=['GET'])
@company_required
def get_company_stats():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)

    # get all drive ids of this company
    drive_id_list = [d.id for d in comp.drives]
    total_drives = len(drive_id_list)

    # count total applications received across all drives
    if drive_id_list:
        total_applications = Application.query.filter(
            Application.drive_id.in_(drive_id_list)
        ).count()
    else:
        total_applications = 0

    # count shortlisted students
    if drive_id_list:
        shortlisted = Application.query.filter(
            Application.drive_id.in_(drive_id_list),
            Application.application_status.in_(['shortlisted', 'interview', 'selected'])
        ).count()
    else:
        shortlisted = 0

    # count selected students
    if drive_id_list:
        selected = Application.query.filter(
            Application.drive_id.in_(drive_id_list),
            Application.application_status == 'selected'
        ).count()
    else:
        selected = 0

    return jsonify({
        'stats': [
            {'label': 'Total Drives', 'value': str(total_drives), 'icon': 'bi-megaphone', 'tone': 'primary'},
            {'label': 'Applications Received', 'value': str(total_applications), 'icon': 'bi-inbox', 'tone': 'success'},
            {'label': 'Shortlisted Students', 'value': str(shortlisted), 'icon': 'bi-person-check', 'tone': 'warning'},
            {'label': 'Selected Students', 'value': str(selected), 'icon': 'bi-trophy', 'tone': 'danger'}
        ]
    }), 200


# ---- PROFILE ----

@company_bp.route('/profile', methods=['GET'])
@company_required
def get_company_profile():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    return jsonify({'company': comp.to_dict()}), 200


@company_bp.route('/profile', methods=['PUT'])
@company_required
def update_company_profile():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # update allowed fields
    allowed_fields = ['company_name', 'industry', 'website', 'description',
                      'contact_person', 'contact_email', 'contact_phone', 'city', 'address']
    for field in allowed_fields:
        if field in data:
            setattr(comp, field, data[field])

    if 'name' in data:
        comp.user.name = data['name']

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'company': comp.to_dict()}), 200


# ---- PLACEMENT DRIVES ----

@company_bp.route('/drives', methods=['GET'])
@company_required
def get_company_drives():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)

    # get all drives posted by this company
    drives = PlacementDrive.query.filter_by(company_id=comp.id).order_by(
        PlacementDrive.created_at.desc()
    ).all()

    return jsonify({'drives': [d.to_dict() for d in drives]}), 200


@company_bp.route('/drives', methods=['POST'])
@company_required
def create_new_drive():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)

    # company must be approved before posting drives
    if comp.approval_status != 'approved':
        return jsonify({'error': 'Your company must be approved by admin before creating drives'}), 403

    data = request.get_json()

    if not data or not data.get('job_role'):
        return jsonify({'error': 'job_role is required'}), 400

    # handle deadline date conversion
    deadline_date = None
    if data.get('deadline'):
        try:
            deadline_date = date.fromisoformat(data['deadline'])
        except ValueError:
            return jsonify({'error': 'Deadline date format should be YYYY-MM-DD'}), 400

    new_drive = PlacementDrive(
        company_id=comp.id,
        title=data.get('title', data['job_role']),
        job_role=data['job_role'],
        package=data.get('package'),
        eligibility=data.get('eligibility'),
        openings=data.get('openings', 1),
        deadline=deadline_date,
        description=data.get('description'),
        status='pending'   # admin needs to approve before it goes live
    )

    db.session.add(new_drive)
    db.session.commit()

    return jsonify({'message': 'Drive submitted for admin approval', 'drive': new_drive.to_dict()}), 201


@company_bp.route('/drives/<int:drive_id>', methods=['GET'])
@company_required
def get_single_drive(drive_id):
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)

    # only show drives that belong to this company
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=comp.id).first_or_404()
    return jsonify({'drive': drive.to_dict()}), 200


@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@company_required
def update_drive(drive_id):
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=comp.id).first_or_404()
    data = request.get_json()

    updatable = ['title', 'job_role', 'package', 'eligibility', 'openings', 'description']
    for field in updatable:
        if field in data:
            setattr(drive, field, data[field])

    if 'deadline' in data and data['deadline']:
        try:
            drive.deadline = date.fromisoformat(data['deadline'])
        except ValueError:
            return jsonify({'error': 'Deadline format should be YYYY-MM-DD'}), 400

    if 'status' in data and data['status'] in ('pending', 'open', 'closed'):
        drive.status = data['status']

    db.session.commit()
    return jsonify({'message': 'Drive updated', 'drive': drive.to_dict()}), 200


@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@company_required
def delete_drive(drive_id):
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=comp.id).first_or_404()
    db.session.delete(drive)
    db.session.commit()
    return jsonify({'message': 'Drive deleted'}), 200


# ---- APPLICATIONS ----

@company_bp.route('/applications', methods=['GET'])
@company_required
def get_received_applications():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)

    drive_id_list = [d.id for d in comp.drives]

    status_filter = request.args.get('status', '').strip()
    drive_filter = request.args.get('drive_id', '').strip()

    query = Application.query.filter(Application.drive_id.in_(drive_id_list))

    if status_filter:
        query = query.filter(Application.application_status == status_filter.lower())

    if drive_filter:
        query = query.filter(Application.drive_id == int(drive_filter))

    apps = query.order_by(Application.applied_at.desc()).all()
    return jsonify({'applications': [a.to_dict() for a in apps]}), 200


@company_bp.route('/applications/<int:app_id>/shortlist', methods=['PUT'])
@company_required
def shortlist_student(app_id):
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    app = Application.query.get_or_404(app_id)

    drive_id_list = [d.id for d in comp.drives]
    if app.drive_id not in drive_id_list:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    app.application_status = 'shortlisted'

    # update student placement status
    if app.student:
        if app.student.placement_status not in ('Placed', 'Interview'):
            app.student.placement_status = 'Applied'

    db.session.commit()
    return jsonify({'message': 'Student shortlisted', 'application': app.to_dict()}), 200


@company_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@company_required
def reject_application(app_id):
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    app = Application.query.get_or_404(app_id)

    drive_id_list = [d.id for d in comp.drives]
    if app.drive_id not in drive_id_list:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    app.application_status = 'rejected'
    db.session.commit()
    return jsonify({'message': 'Application rejected'}), 200


# ---- INTERVIEWS ----

@company_bp.route('/interviews', methods=['GET'])
@company_required
def get_scheduled_interviews():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    drive_id_list = [d.id for d in comp.drives]

    all_apps = Application.query.filter(
        Application.drive_id.in_(drive_id_list)
    ).all()

    interview_list = []
    for app in all_apps:
        if app.interview:
            i_data = app.interview.to_dict()
            i_data['student_name'] = app.student.user.name if app.student and app.student.user else ''
            i_data['drive_title'] = app.drive.title if app.drive else ''
            interview_list.append(i_data)

    return jsonify({'interviews': interview_list}), 200


@company_bp.route('/interviews', methods=['POST'])
@company_required
def schedule_interview():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    data = request.get_json()

    app_id = data.get('application_id')
    if not app_id:
        return jsonify({'error': 'application_id is required'}), 400

    app = Application.query.get_or_404(app_id)

    drive_id_list = [d.id for d in comp.drives]
    if app.drive_id not in drive_id_list:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    # create or update interview record
    if app.interview:
        interview_record = app.interview
    else:
        interview_record = Interview(application_id=app_id)
        db.session.add(interview_record)

    if data.get('interview_date'):
        try:
            interview_record.interview_date = date.fromisoformat(data['interview_date'])
        except ValueError:
            return jsonify({'error': 'Interview date format should be YYYY-MM-DD'}), 400

    interview_record.interview_time = data.get('interview_time')
    interview_record.interview_mode = data.get('interview_mode', 'online')
    interview_record.interview_link = data.get('interview_link')
    interview_record.round_name = data.get('round_name')
    interview_record.remarks = data.get('remarks')

    # update application status to interview
    app.application_status = 'interview'
    if app.student:
        app.student.placement_status = 'Interview'

    db.session.commit()
    return jsonify({'message': 'Interview scheduled successfully', 'interview': interview_record.to_dict()}), 201


# ---- RESULTS ----

@company_bp.route('/results', methods=['GET'])
@company_required
def get_result_candidates():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    drive_id_list = [d.id for d in comp.drives]

    # get applications that are in interview or shortlisted stage
    apps = Application.query.filter(
        Application.drive_id.in_(drive_id_list),
        Application.application_status.in_(['interview', 'shortlisted'])
    ).all()

    candidates = []
    for app in apps:
        candidates.append({
            'application_id': app.id,
            'student_name': app.student.user.name if app.student and app.student.user else '',
            'drive_title': app.drive.title if app.drive else '',
            'drive_role': app.drive.job_role if app.drive else '',
            'application_status': app.application_status,
            'result': app.result.to_dict() if app.result else None
        })

    return jsonify({'candidates': candidates}), 200


@company_bp.route('/results/publish', methods=['POST'])
@company_required
def publish_result():
    uid = get_jwt_identity()
    comp = get_company_by_user(uid)
    data = request.get_json()

    app_id = data.get('application_id')
    result_status = data.get('result_status')

    if not app_id:
        return jsonify({'error': 'application_id is required'}), 400

    if result_status not in ('selected', 'rejected'):
        return jsonify({'error': 'result_status must be selected or rejected'}), 400

    app = Application.query.get_or_404(app_id)

    drive_id_list = [d.id for d in comp.drives]
    if app.drive_id not in drive_id_list:
        return jsonify({'error': 'This application does not belong to your drives'}), 403

    # update or create result record
    if app.result:
        app.result.result_status = result_status
        app.result.remarks = data.get('remarks')
    else:
        new_result = Result(
            application_id=app_id,
            result_status=result_status,
            remarks=data.get('remarks')
        )
        db.session.add(new_result)

    # update application status
    app.application_status = result_status

    # if selected, mark student as placed
    if result_status == 'selected' and app.student:
        app.student.placement_status = 'Placed'

    db.session.commit()
    return jsonify({'message': 'Result published: ' + result_status}), 200
