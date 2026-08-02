from flask import Blueprint, request, jsonify, send_from_directory
from middleware.auth_middleware import admin_required
from services.admin_service import AdminService
from cache import cache
from cache.decorators import cache_response

admin_bp = Blueprint('admin_routes', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:stats', ttl=300)
def get_dashboard_stats():
    stats_list = AdminService.get_dashboard_stats()
    return jsonify({'stats': stats_list}), 200

@admin_bp.route('/activities', methods=['GET'])
@admin_required
@cache_response(lambda: 'admin:activities', ttl=120)
def get_recent_activities():
    activities_log = AdminService.get_recent_activities()
    return jsonify({'activities': activities_log}), 200

@admin_bp.route('/applications', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:applications:{request.args.get('search','').strip().lower()}:{request.args.get('status','').strip().lower()}:{request.args.get('page',1)}",
    ttl=120
)
def get_all_applications():
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))
    
    result = AdminService.get_applications(search_term, status_filter, page_num, records_per_page)
    return jsonify(result), 200

@admin_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@admin_required
def update_application_status(app_id):
    payload = request.get_json() or {}
    new_status = payload.get('status')
    
    app_dict = AdminService.update_application_status(app_id, new_status)
    
    cache.delete_pattern('admin:applications:*')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({'message': f"Application status updated to {new_status}", 'application': app_dict}), 200

@admin_bp.route('/students', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:students:{request.args.get('search','').strip().lower()}:{request.args.get('status','').strip().lower()}:{request.args.get('page',1)}",
    ttl=180
)
def get_all_students():
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))
    
    result = AdminService.get_students(search_term, status_filter, page_num, records_per_page)
    return jsonify(result), 200

@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:student:{request.view_args.get('student_id')}", ttl=180)
def get_student_detail(student_id):
    student_dict = AdminService.get_student_detail(student_id)
    return jsonify({'student': student_dict}), 200

@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    payload = request.get_json() or {}
    student_dict = AdminService.update_student(student_id, payload)
    
    cache.delete_pattern('admin:students:*')
    cache.delete(f'admin:student:{student_id}')
    cache.delete('admin:stats')
    
    return jsonify({'message': 'Student updated', 'student': student_dict}), 200

@admin_bp.route('/students/<int:student_id>/status', methods=['PUT'])
@admin_required
def change_student_status(student_id):
    payload = request.get_json() or {}
    new_status = payload.get('status')
    
    AdminService.change_student_status(student_id, new_status)
    
    cache.delete_pattern('admin:students:*')
    cache.delete(f'admin:student:{student_id}')
    
    return jsonify({'message': f"Student status updated to {new_status}"}), 200

@admin_bp.route('/companies', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:companies:{request.args.get('search','').strip().lower()}:{request.args.get('status','').strip().lower()}:{request.args.get('page',1)}",
    ttl=180
)
def get_all_companies():
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))
    
    result = AdminService.get_companies(search_term, status_filter, page_num, records_per_page)
    return jsonify(result), 200

@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:company:{request.view_args.get('company_id')}", ttl=180)
def get_company_detail(company_id):
    company_dict = AdminService.get_company_detail(company_id)
    return jsonify({'company': company_dict}), 200

@admin_bp.route('/companies/<int:company_id>/approve', methods=['PUT'])
@admin_required
def approve_company(company_id):
    AdminService.update_company_approval(company_id, 'approved')
    
    cache.delete_pattern('admin:companies:*')
    cache.delete(f'admin:company:{company_id}')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({'message': 'Company approved'}), 200

@admin_bp.route('/companies/<int:company_id>/reject', methods=['PUT'])
@admin_required
def reject_company(company_id):
    AdminService.update_company_approval(company_id, 'rejected')
    
    cache.delete_pattern('admin:companies:*')
    cache.delete(f'admin:company:{company_id}')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({'message': 'Company rejected'}), 200

@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['PUT'])
@admin_required
def blacklist_company(company_id):
    payload = request.get_json() or {}
    flag = payload.get('blacklisted', True)
    
    AdminService.update_company_blacklist(company_id, flag)
    
    cache.delete_pattern('admin:companies:*')
    cache.delete(f'admin:company:{company_id}')
    cache.delete('admin:stats')
    
    status_str = 'blacklisted' if flag else 'unblacklisted'
    return jsonify({'message': f"Company {status_str}"}), 200

@admin_bp.route('/drives', methods=['GET'])
@admin_required
@cache_response(
    lambda: f"admin:drives:{request.args.get('search','').strip().lower()}:{request.args.get('status','').strip().lower()}:{request.args.get('page',1)}",
    ttl=180
)
def get_all_drives():
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    page_num = int(request.args.get('page', 1))
    records_per_page = int(request.args.get('per_page', 20))
    
    result = AdminService.get_drives(search_term, status_filter, page_num, records_per_page)
    return jsonify(result), 200

@admin_bp.route('/drives/<int:drive_id>', methods=['GET'])
@admin_required
@cache_response(lambda: f"admin:drive:{request.view_args.get('drive_id')}", ttl=180)
def get_drive_detail(drive_id):
    drive_dict = AdminService.get_drive_detail(drive_id)
    return jsonify({'drive': drive_dict}), 200

@admin_bp.route('/drives/<int:drive_id>/approve', methods=['PUT'])
@admin_required
def approve_drive(drive_id):
    AdminService.update_drive_status(drive_id, 'open')
    
    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({'message': 'Drive approved and is now open'}), 200

@admin_bp.route('/drives/<int:drive_id>/reject', methods=['PUT'])
@admin_required
def reject_drive(drive_id):
    AdminService.update_drive_status(drive_id, 'rejected')
    
    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')
    
    return jsonify({'message': 'Drive rejected'}), 200

@admin_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@admin_required
def close_drive(drive_id):
    AdminService.update_drive_status(drive_id, 'closed')
    
    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({'message': 'Placement drive closed successfully'}), 200

@admin_bp.route('/drives/<int:drive_id>/status', methods=['PUT'])
@admin_required
def update_drive_status(drive_id):
    payload = request.get_json() or {}
    new_status = payload.get('status', '').lower()
    
    AdminService.update_drive_status(drive_id, new_status)
    
    cache.delete_pattern('admin:drives:*')
    cache.delete(f'admin:drive:{drive_id}')
    cache.delete('admin:stats')
    
    return jsonify({'message': f"Drive status changed to {new_status}"}), 200

@admin_bp.route('/resumes/<filename>', methods=['GET'])
@admin_required
def download_resume(filename):
    from config import Config
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
