from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import company_required
from services.company_service import CompanyService
from cache import cache
from cache.decorators import cache_response

company_bp = Blueprint('company_routes', __name__, url_prefix='/api/company')

@company_bp.route('/stats', methods=['GET'])
@company_required
@cache_response(lambda: f"company:stats:{get_jwt_identity()}", ttl=120)
def get_company_stats():
    uid = get_jwt_identity()
    stats = CompanyService.get_stats(uid)
    return jsonify({'stats': stats}), 200

@company_bp.route('/profile', methods=['GET'])
@company_required
@cache_response(lambda: f"company:profile:{get_jwt_identity()}", ttl=300)
def get_company_profile():
    uid = get_jwt_identity()
    profile = CompanyService.get_profile(uid)
    return jsonify({'company': profile}), 200

@company_bp.route('/profile', methods=['PUT'])
@company_required
def update_company_profile():
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    profile = CompanyService.update_profile(uid, payload)
    
    cache.delete(f'company:profile:{uid}')
    cache.delete(f'company:stats:{uid}')
    
    return jsonify({'message': 'Profile updated', 'company': profile}), 200

@company_bp.route('/drives', methods=['GET'])
@company_required
@cache_response(lambda: f"company:drives:{get_jwt_identity()}", ttl=120)
def get_company_drives():
    uid = get_jwt_identity()
    drives = CompanyService.get_drives(uid)
    return jsonify({'drives': drives}), 200

@company_bp.route('/drives', methods=['POST'])
@company_required
def create_new_drive():
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    drive = CompanyService.create_drive(uid, payload)
    
    cache.delete(f'company:drives:{uid}')
    cache.delete(f'company:stats:{uid}')
    cache.delete_pattern('admin:drives:*')
    cache.delete('admin:activities')
    
    return jsonify({'message': 'Drive submitted for admin approval', 'drive': drive}), 201

@company_bp.route('/drives/<int:drive_id>', methods=['GET'])
@company_required
def get_single_drive(drive_id):
    uid = get_jwt_identity()
    drive = CompanyService.get_drive(uid, drive_id)
    return jsonify({'drive': drive}), 200

@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@company_required
def update_drive(drive_id):
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    drive = CompanyService.update_drive(uid, drive_id, payload)
    
    cache.delete(f'company:drives:{uid}')
    cache.delete_pattern('admin:drives:*')
    
    return jsonify({'message': 'Drive updated', 'drive': drive}), 200

@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@company_required
def delete_drive(drive_id):
    uid = get_jwt_identity()
    CompanyService.delete_drive(uid, drive_id)
    
    cache.delete(f'company:drives:{uid}')
    cache.delete(f'company:stats:{uid}')
    cache.delete_pattern('admin:drives:*')
    cache.delete('admin:stats')
    
    return jsonify({'message': 'Drive deleted'}), 200

@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@company_required
def close_drive(drive_id):
    uid = get_jwt_identity()
    drive = CompanyService.close_drive(uid, drive_id)
    
    cache.delete(f'company:drives:{uid}')
    cache.delete(f'company:stats:{uid}')
    cache.delete_pattern('admin:drives:*')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({'message': 'Placement drive closed', 'drive': drive}), 200

@company_bp.route('/applications', methods=['GET'])
@company_required
def get_received_applications():
    uid = get_jwt_identity()
    status_filter = request.args.get('status', '').strip()
    drive_filter = request.args.get('drive_id', '').strip()
    
    apps = CompanyService.get_received_applications(uid, status_filter, drive_filter)
    return jsonify({'applications': apps}), 200

@company_bp.route('/applications/<int:app_id>/shortlist', methods=['PUT'])
@company_required
def shortlist_student(app_id):
    uid = get_jwt_identity()
    app = CompanyService.shortlist_student(uid, app_id)
    
    cache.delete(f'company:stats:{uid}')
    
    return jsonify({'message': 'Student shortlisted', 'application': app}), 200

@company_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@company_required
def reject_application(app_id):
    uid = get_jwt_identity()
    app = CompanyService.reject_application(uid, app_id)
    cache.delete(f'company:stats:{uid}')
    return jsonify({'message': 'Application rejected', 'application': app}), 200

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@company_required
def update_application_status(app_id):
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    new_status = payload.get('status')
    
    app = CompanyService.update_application_status(uid, app_id, new_status)
    cache.delete(f'company:stats:{uid}')
    
    return jsonify({'message': f"Application status updated to {new_status}", 'application': app}), 200

@company_bp.route('/interviews', methods=['GET'])
@company_required
def get_scheduled_interviews():
    uid = get_jwt_identity()
    interviews = CompanyService.get_scheduled_interviews(uid)
    return jsonify({'interviews': interviews}), 200

@company_bp.route('/interviews', methods=['POST'])
@company_required
def schedule_interview():
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    interview = CompanyService.schedule_interview(uid, payload)
    
    cache.delete(f'company:stats:{uid}')
    app_id = payload.get('application_id')
    
    from models.application import Application
    from models import db
    app_record = db.session.query(Application).filter(Application.id == app_id).first()
    if app_record and app_record.student:
        cache.delete(f'student:stats:{app_record.student.user_id}')
        
    return jsonify({'message': 'Interview scheduled successfully', 'interview': interview}), 201

@company_bp.route('/interviews/<int:interview_id>/email', methods=['POST'])
@company_required
def send_interview_email(interview_id):
    uid = get_jwt_identity()
    CompanyService.send_interview_email(uid, interview_id)
    return jsonify({'message': 'Interview reminder email sent successfully to the candidate'}), 200

@company_bp.route('/results', methods=['GET'])
@company_required
def get_result_candidates():
    uid = get_jwt_identity()
    candidates = CompanyService.get_result_candidates(uid)
    return jsonify({'candidates': candidates}), 200

@company_bp.route('/results/publish', methods=['POST'])
@company_required
def publish_result():
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    CompanyService.publish_result(uid, payload)
    
    cache.delete(f'company:stats:{uid}')
    cache.delete('admin:stats')
    cache.delete('admin:report_stats')
    
    app_id = payload.get('application_id')
    from models.application import Application
    from models import db
    app_record = db.session.query(Application).filter(Application.id == app_id).first()
    if app_record and app_record.student:
        cache.delete(f'student:stats:{app_record.student.user_id}')
        
    return jsonify({'message': f"Result published: {payload.get('result_status')}"}), 200
