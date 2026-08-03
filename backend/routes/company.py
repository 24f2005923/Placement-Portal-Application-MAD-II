from flask import Blueprint
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import company_required
from services.company_service import CompanyService
from cache.decorators import cache_response
from utils.cache_manager import CacheManager
from utils.request_helpers import json_payload, query_text
from utils.responses import success_response, created_response

company_bp = Blueprint('company_routes', __name__, url_prefix='/api/company')

@company_bp.route('/stats', methods=['GET'])
@company_required
@cache_response(lambda: f"company:stats:{get_jwt_identity()}", ttl=120)
def get_company_stats():
    uid = get_jwt_identity()
    stats = CompanyService.get_stats(uid)
    return success_response({'stats': stats})

@company_bp.route('/profile', methods=['GET'])
@company_required
@cache_response(lambda: f"company:profile:{get_jwt_identity()}", ttl=300)
def get_company_profile():
    uid = get_jwt_identity()
    profile = CompanyService.get_profile(uid)
    return success_response({'company': profile})

@company_bp.route('/profile', methods=['PUT'])
@company_required
def update_company_profile():
    uid = get_jwt_identity()
    payload = json_payload()
    profile = CompanyService.update_profile(uid, payload)
    
    CacheManager.invalidate_company(company_id=None, user_id=uid)
    
    return success_response({'company': profile}, 'Profile updated')

@company_bp.route('/drives', methods=['GET'])
@company_required
@cache_response(lambda: f"company:drives:{get_jwt_identity()}", ttl=120)
def get_company_drives():
    uid = get_jwt_identity()
    drives = CompanyService.get_drives(uid)
    return success_response({'drives': drives})

@company_bp.route('/drives', methods=['POST'])
@company_required
def create_new_drive():
    uid = get_jwt_identity()
    payload = json_payload()
    drive = CompanyService.create_drive(uid, payload)
    
    CacheManager.invalidate_drive(drive_id=None, company_user_id=uid)
    CacheManager.invalidate_admin_stats()
    
    return created_response({'drive': drive}, 'Placement drive created successfully')

@company_bp.route('/drives/<int:drive_id>', methods=['GET'])
@company_required
def get_single_drive(drive_id):
    uid = get_jwt_identity()
    drive = CompanyService.get_drive(uid, drive_id)
    return success_response({'drive': drive})

@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@company_required
def update_drive(drive_id):
    uid = get_jwt_identity()
    payload = json_payload()
    drive = CompanyService.update_drive(uid, drive_id, payload)
    
    CacheManager.invalidate_drive(drive_id, company_user_id=uid)
    
    return success_response({'drive': drive}, 'Drive updated')

@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@company_required
def delete_drive(drive_id):
    uid = get_jwt_identity()
    CompanyService.delete_drive(uid, drive_id)
    
    CacheManager.invalidate_drive(drive_id, company_user_id=uid)
    CacheManager.invalidate_admin_stats()
    
    return success_response(message='Drive deleted')

@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@company_required
def close_drive(drive_id):
    uid = get_jwt_identity()
    drive = CompanyService.close_drive(uid, drive_id)
    
    CacheManager.invalidate_drive(drive_id, company_user_id=uid)
    CacheManager.invalidate_admin_stats()
    
    return success_response({'drive': drive}, 'Placement drive closed')

@company_bp.route('/applications', methods=['GET'])
@company_required
def get_received_applications():
    uid = get_jwt_identity()
    status_filter = query_text('status')
    drive_filter = query_text('drive_id')
    
    apps = CompanyService.get_received_applications(uid, status_filter, drive_filter)
    return success_response({'applications': apps})

@company_bp.route('/applications/<int:app_id>/shortlist', methods=['PUT'])
@company_required
def shortlist_student(app_id):
    uid = get_jwt_identity()
    app = CompanyService.shortlist_student(uid, app_id)
    
    CacheManager.invalidate_company(company_id=None, user_id=uid)
    
    return success_response({'application': app}, 'Student shortlisted')

@company_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@company_required
def reject_application(app_id):
    uid = get_jwt_identity()
    app = CompanyService.reject_application(uid, app_id)
    CacheManager.invalidate_company(company_id=None, user_id=uid)
    return success_response({'application': app}, 'Application rejected')

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@company_required
def update_application_status(app_id):
    uid = get_jwt_identity()
    payload = json_payload()
    new_status = payload.get('status')
    
    app = CompanyService.update_application_status(uid, app_id, new_status)
    CacheManager.invalidate_company(company_id=None, user_id=uid)
    
    return success_response({'application': app}, f"Application status updated to {new_status}")

@company_bp.route('/interviews', methods=['GET'])
@company_required
def get_scheduled_interviews():
    uid = get_jwt_identity()
    interviews = CompanyService.get_scheduled_interviews(uid)
    return success_response({'interviews': interviews})

@company_bp.route('/interviews', methods=['POST'])
@company_required
def schedule_interview():
    uid = get_jwt_identity()
    payload = json_payload()
    interview = CompanyService.schedule_interview(uid, payload)
    
    CacheManager.invalidate_company(company_id=None, user_id=uid)
    CacheManager.invalidate_application_student(payload.get('application_id'))
        
    return created_response({'interview': interview}, 'Interview scheduled successfully')

@company_bp.route('/interviews/<int:interview_id>/email', methods=['POST'])
@company_required
def send_interview_email(interview_id):
    uid = get_jwt_identity()
    CompanyService.send_interview_email(uid, interview_id)
    return success_response(message='Interview reminder email sent successfully to the candidate')

@company_bp.route('/results', methods=['GET'])
@company_required
def get_result_candidates():
    uid = get_jwt_identity()
    candidates = CompanyService.get_result_candidates(uid)
    return success_response({'candidates': candidates})

@company_bp.route('/results/publish', methods=['POST'])
@company_required
def publish_result():
    uid = get_jwt_identity()
    payload = json_payload()
    CompanyService.publish_result(uid, payload)
    
    CacheManager.invalidate_company(company_id=None, user_id=uid)
    CacheManager.invalidate_admin_stats()
    CacheManager.invalidate_admin_report_stats()
    
    CacheManager.invalidate_application_student(payload.get('application_id'))
        
    return success_response(message=f"Result published: {payload.get('result_status')}")
