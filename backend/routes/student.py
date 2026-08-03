import os

from flask import Blueprint, request, send_from_directory, current_app
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import student_required
from services.student_service import StudentService
from cache.decorators import cache_response
from utils.cache_manager import CacheManager
from utils.request_helpers import json_payload, query_text
from utils.responses import success_response, error_response, created_response
from utils.task_runner import async_result_response, dispatch_task, task_dispatch_response

student_bp = Blueprint('student_routes', __name__, url_prefix='/api/student')

@student_bp.route('/stats', methods=['GET'])
@student_required
@cache_response(lambda: f"student:stats:{get_jwt_identity()}", ttl=120)
def get_student_stats():
    uid = get_jwt_identity()
    stats = StudentService.get_stats(uid)
    return success_response({'stats': stats})

@student_bp.route('/profile', methods=['GET'])
@student_required
@cache_response(lambda: f"student:profile:{get_jwt_identity()}", ttl=300)
def get_profile():
    uid = get_jwt_identity()
    profile = StudentService.get_profile(uid)
    return success_response({'student': profile})

@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    uid = get_jwt_identity()
    payload = json_payload()
    profile = StudentService.update_profile(uid, payload)
    
    CacheManager.invalidate_student(student_id=None, user_id=uid)
    
    return success_response({'student': profile}, 'Profile updated successfully')

@student_bp.route('/resume', methods=['POST'])
@student_required
def upload_resume():
    uid = get_jwt_identity()
    if 'resume' not in request.files:
        return error_response('No file uploaded. Use field name "resume"', 400)

    file_obj = request.files['resume']
    saved_filename = StudentService.upload_resume(uid, file_obj)
    
    CacheManager.invalidate_student(student_id=None, user_id=uid)
    
    return success_response({
        'resume_path': saved_filename,
        'resume_url': f"/api/student/resume/{saved_filename}"
    }, 'Resume uploaded successfully')

@student_bp.route('/resume/<filename>', methods=['GET'])
def get_resume(filename):
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    elif 'token' in request.args:
        token = request.args.get('token')

    if token:
        try:
            from flask_jwt_extended import decode_token
            decode_token(token)
        except Exception:
            return error_response('Invalid or expired token', 401)
    else:
        return error_response('Missing authorization token', 401)

    from flask import current_app
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@student_bp.route('/drives', methods=['GET'])
@student_required
@cache_response(
    lambda: f"student:drives:{get_jwt_identity()}:{query_text('search').lower()}",
    ttl=120
)
def list_open_drives():
    uid = get_jwt_identity()
    search_query = query_text('search')
    drives = StudentService.list_open_drives(uid, search_query)
    return success_response({'drives': drives})

@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@student_required
def get_drive_details(drive_id):
    uid = get_jwt_identity()
    drive_dict = StudentService.get_drive_details(uid, drive_id)
    return success_response({'drive': drive_dict})

@student_bp.route('/applications', methods=['POST'])
@student_required
def apply_for_drive():
    uid = get_jwt_identity()
    resume_file = None
    if request.is_json:
        payload = json_payload()
        drive_id = payload.get('drive_id')
        cover_note = payload.get('cover_note')
    else:
        drive_id = request.form.get('drive_id')
        cover_note = request.form.get('cover_note')
        resume_file = request.files.get('resume')
    
    if not drive_id:
        return error_response('drive_id is required', 400)

    app = StudentService.apply_for_drive(uid, int(drive_id), cover_note, resume_file=resume_file)
    
    CacheManager.invalidate_student(student_id=None, user_id=uid)
    CacheManager.invalidate_application()
    CacheManager.invalidate_admin_stats()
    
    return created_response({
        'application': app
    }, 'Application submitted successfully')

@student_bp.route('/applications', methods=['GET'])
@student_required
def get_my_applications():
    uid = get_jwt_identity()
    apps = StudentService.get_my_applications(uid)
    return success_response({'applications': apps})

@student_bp.route('/applications/export', methods=['POST'])
@student_required
def export_my_applications():
    from tasks.csv_exports import export_student_applications_csv

    uid = get_jwt_identity()
    student = StudentService.get_student_by_user(uid)
    notify_email = student.user.email if student.user else None

    dispatched = dispatch_task(
        export_student_applications_csv,
        user_id=int(uid),
        requested_by_email=notify_email,
    )

    return task_dispatch_response(
        dispatched,
        queued_message='Application history CSV export has been queued.',
        completed_message='Application history CSV export completed successfully.',
        status_url_prefix='/api/student/applications/export/status',
        download_url_builder=_student_application_export_download_url,
    )

@student_bp.route('/applications/export/status/<task_id>', methods=['GET'])
@student_required
def get_application_export_status(task_id):
    from celery_app import celery

    task_result = celery.AsyncResult(task_id)
    return async_result_response(
        task_id,
        task_result,
        download_url_builder=_student_application_export_download_url,
        pending_message='Application history CSV export is queued / processing...',
    )

@student_bp.route('/applications/export/download/<filename>', methods=['GET'])
@student_required
def download_application_export(filename):
    uid = get_jwt_identity()
    student = StudentService.get_student_by_user(uid)

    expected_prefix = f'student_applications_{student.id}_'
    if not filename.endswith('.csv') or not filename.startswith(expected_prefix):
        return error_response('Export file not found', 404)

    exports_dir = current_app.config['EXPORTS_FOLDER']
    file_path = os.path.join(exports_dir, filename)
    if not os.path.isfile(file_path):
        return error_response('Export file not found', 404)

    return send_from_directory(exports_dir, filename, as_attachment=True)

@student_bp.route('/applications/<int:app_id>/offer-letter', methods=['GET'])
def download_offer_letter(app_id):
    from flask import Response
    from flask_jwt_extended import decode_token

    uid = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = request.args.get('token')

    if token:
        try:
            decoded_token = decode_token(token)
        except Exception:
            return error_response('Invalid or expired token', 401)
        if decoded_token.get('role') != 'student':
            return error_response('Access denied: Student account required', 403)
        uid = decoded_token.get('sub')
    else:
        return error_response('Missing authorization token', 401)

    html_doc, filename = StudentService.generate_offer_letter(uid, app_id)
    
    response = Response(html_doc, mimetype='text/html')
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@student_bp.route('/interviews', methods=['GET'])
@student_required
def get_my_interviews():
    uid = get_jwt_identity()
    interviews = StudentService.get_my_interviews(uid)
    return success_response({'interviews': interviews})

@student_bp.route('/history', methods=['GET'])
@student_required
def get_placement_history():
    uid = get_jwt_identity()
    history = StudentService.get_placement_history(uid)
    return success_response({'history': history})

def _student_application_export_download_url(result):
    filename = (result or {}).get('filename')
    return f'/api/student/applications/export/download/{filename}' if filename else None
