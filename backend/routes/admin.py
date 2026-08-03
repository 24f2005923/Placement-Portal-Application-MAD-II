from flask import Blueprint, request, send_from_directory
from middleware.auth_middleware import admin_required
from services.admin_service import AdminService
from cache.decorators import cache_response
from utils.cache_manager import CacheManager
from utils.request_helpers import json_payload, query_cache_key, search_status_pagination
from utils.responses import success_response

admin_bp = Blueprint('admin_routes', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:stats', ttl=300)
def get_dashboard_stats():
    stats_list = AdminService.get_dashboard_stats()
    return success_response({'stats': stats_list})

@admin_bp.route('/activities', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:activities', ttl=120)
def get_recent_activities():
    activities_log = AdminService.get_recent_activities()
    return success_response({'activities': activities_log})

@admin_bp.route('/applications', methods=['GET'])
@admin_required
@cache_response(
    lambda: query_cache_key('admin:applications', 'search', 'status'),
    ttl=120
)
def get_all_applications():
    search_term, status_filter, page_num, records_per_page = search_status_pagination()
    result = AdminService.get_applications(search_term, status_filter, page_num, records_per_page)
    return success_response(result)

@admin_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@admin_required
def update_application_status(app_id):
    payload = json_payload()
    new_status = payload.get('status')
    
    app_dict = AdminService.update_application_status(app_id, new_status)
    
    CacheManager.invalidate_application()
    CacheManager.invalidate_admin_stats()
    
    return success_response({'application': app_dict}, f"Application status updated to {new_status}")

@admin_bp.route('/students', methods=['GET'])
@admin_required
@cache_response(
    lambda: query_cache_key('admin:students', 'search', 'status'),
    ttl=180
)
def get_all_students():
    search_term, status_filter, page_num, records_per_page = search_status_pagination()
    result = AdminService.get_students(search_term, status_filter, page_num, records_per_page)
    return success_response(result)

@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:student:{request.view_args.get('student_id')}", ttl=180)
def get_student_detail(student_id):
    student_dict = AdminService.get_student_detail(student_id)
    return success_response({'student': student_dict})

@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    payload = json_payload()
    student_dict = AdminService.update_student(student_id, payload)
    
    CacheManager.invalidate_student(student_id)
    CacheManager.invalidate_admin_stats()
    
    return success_response({'student': student_dict}, 'Student updated')

@admin_bp.route('/students/<int:student_id>/status', methods=['PUT'])
@admin_required
def change_student_status(student_id):
    payload = json_payload()
    new_status = payload.get('status')
    
    AdminService.change_student_status(student_id, new_status)
    
    CacheManager.invalidate_student(student_id)
    
    return success_response(message=f"Student status updated to {new_status}")

@admin_bp.route('/companies', methods=['GET'])
@admin_required
@cache_response(
    lambda: query_cache_key('admin:companies', 'search', 'status'),
    ttl=180
)
def get_all_companies():
    search_term, status_filter, page_num, records_per_page = search_status_pagination()
    result = AdminService.get_companies(search_term, status_filter, page_num, records_per_page)
    return success_response(result)

@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:company:{request.view_args.get('company_id')}", ttl=180)
def get_company_detail(company_id):
    company_dict = AdminService.get_company_detail(company_id)
    return success_response({'company': company_dict})

@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@admin_required
def approve_company(company_id):
    AdminService.update_company_approval(company_id, 'approved')
    
    CacheManager.invalidate_company(company_id)
    CacheManager.invalidate_admin_stats()
    
    return success_response(message='Company approved')

@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@admin_required
def reject_company(company_id):
    AdminService.update_company_approval(company_id, 'rejected')
    
    CacheManager.invalidate_company(company_id)
    CacheManager.invalidate_admin_stats()
    
    return success_response(message='Company rejected')

@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_company(company_id):
    payload = json_payload()
    flag = payload.get('blacklisted', True)
    
    AdminService.blacklist_company(company_id, flag)
    
    CacheManager.invalidate_company(company_id)
    CacheManager.invalidate_admin_stats()
    
    status_str = 'blacklisted' if flag else 'unblacklisted'
    return success_response(message=f"Company {status_str}")

@admin_bp.route('/drives', methods=['GET'])
@admin_required
@cache_response(
    lambda: query_cache_key('admin:drives', 'search', 'status'),
    ttl=180
)
def get_all_drives():
    search_term, status_filter, page_num, records_per_page = search_status_pagination()
    result = AdminService.get_drives(search_term, status_filter, page_num, records_per_page)
    return success_response(result)

@admin_bp.route('/drives/<int:drive_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:drive:{request.view_args.get('drive_id')}", ttl=180)
def get_drive_detail(drive_id):
    drive_dict = AdminService.get_drive_detail(drive_id)
    return success_response({'drive': drive_dict})

@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@admin_required
def approve_drive(drive_id):
    AdminService.update_drive_status(drive_id, 'open')
    
    CacheManager.invalidate_drive(drive_id)
    CacheManager.invalidate_admin_stats()
    
    return success_response(message='Drive approved and is now open')

@admin_bp.route('/drives/<int:drive_id>/reject', methods=['PUT'])
@admin_required
def reject_drive(drive_id):
    AdminService.update_drive_status(drive_id, 'rejected')
    
    CacheManager.invalidate_drive(drive_id)
    
    return success_response(message='Drive rejected')

@admin_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@admin_required
def close_drive(drive_id):
    AdminService.update_drive_status(drive_id, 'closed')
    
    CacheManager.invalidate_drive(drive_id)
    CacheManager.invalidate_admin_stats()
    
    return success_response(message='Placement drive closed successfully')

@admin_bp.route('/drives/<int:drive_id>/status', methods=['PUT'])
@admin_required
def update_drive_status(drive_id):
    payload = json_payload()
    new_status = payload.get('status', '').lower()
    
    AdminService.update_drive_status(drive_id, new_status)
    
    CacheManager.invalidate_drive(drive_id)
    CacheManager.invalidate_admin_stats()
    
    return success_response(message=f"Drive status changed to {new_status}")

@admin_bp.route('/resumes/<filename>', methods=['GET'])
@admin_required
def download_resume(filename):
    from config import Config
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
