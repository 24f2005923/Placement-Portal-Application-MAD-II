from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import get_jwt_identity
from middleware.auth_middleware import student_required
from services.student_service import StudentService
from cache import cache
from cache.decorators import cache_response

student_bp = Blueprint('student_routes', __name__, url_prefix='/api/student')

@student_bp.route('/stats', methods=['GET'])
@student_required
@cache_response(lambda: f"student:stats:{get_jwt_identity()}", ttl=120)
def get_student_stats():
    uid = get_jwt_identity()
    stats = StudentService.get_stats(uid)
    return jsonify({'stats': stats}), 200

@student_bp.route('/profile', methods=['GET'])
@student_required
@cache_response(lambda: f"student:profile:{get_jwt_identity()}", ttl=300)
def get_profile():
    uid = get_jwt_identity()
    profile = StudentService.get_profile(uid)
    return jsonify({'student': profile}), 200

@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    uid = get_jwt_identity()
    payload = request.get_json() or {}
    profile = StudentService.update_profile(uid, payload)
    
    cache.delete(f'student:profile:{uid}')
    cache.delete(f'student:stats:{uid}')
    
    return jsonify({'message': 'Profile updated successfully', 'student': profile}), 200

@student_bp.route('/resume', methods=['POST'])
@student_required
def upload_resume():
    uid = get_jwt_identity()
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded. Use field name "resume"'}), 400

    file_obj = request.files['resume']
    saved_filename = StudentService.upload_resume(uid, file_obj)
    
    cache.delete(f'student:profile:{uid}')
    
    return jsonify({
        'message': 'Resume uploaded successfully',
        'resume_path': saved_filename,
        'resume_url': f"/api/student/resume/{saved_filename}"
    }), 200

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
            return jsonify({'error': 'Invalid or expired token'}), 401
    else:
        return jsonify({'error': 'Missing authorization token'}), 401

    from flask import current_app
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@student_bp.route('/drives', methods=['GET'])
@student_required
@cache_response(
    lambda: f"student:drives:{get_jwt_identity()}:{request.args.get('search','').strip()}",
    ttl=120
)
def list_open_drives():
    uid = get_jwt_identity()
    search_query = request.args.get('search', '').strip()
    drives = StudentService.list_open_drives(uid, search_query)
    return jsonify({'drives': drives}), 200

@student_bp.route('/drives/<int:drive_id>', methods=['GET'])
@student_required
def get_drive_details(drive_id):
    uid = get_jwt_identity()
    drive_dict = StudentService.get_drive_details(uid, drive_id)
    return jsonify({'drive': drive_dict}), 200

@student_bp.route('/applications', methods=['POST'])
@student_required
def apply_for_drive():
    uid = get_jwt_identity()
    resume_file = None
    if request.is_json:
        payload = request.get_json() or {}
        drive_id = payload.get('drive_id')
        cover_note = payload.get('cover_note')
    else:
        drive_id = request.form.get('drive_id')
        cover_note = request.form.get('cover_note')
        resume_file = request.files.get('resume')
    
    if not drive_id:
        return jsonify({'error': 'drive_id is required'}), 400

    app = StudentService.apply_for_drive(uid, int(drive_id), cover_note, resume_file=resume_file)
    
    cache.delete(f'student:stats:{uid}')
    cache.delete_pattern(f'student:drives:{uid}:*')
    cache.delete_pattern('company:applications:*')
    cache.delete_pattern('company:drives:*')
    cache.delete('admin:stats')
    cache.delete('admin:activities')
    
    return jsonify({
        'message': 'Application submitted successfully',
        'application': app
    }), 201

@student_bp.route('/applications', methods=['GET'])
@student_required
def get_my_applications():
    uid = get_jwt_identity()
    apps = StudentService.get_my_applications(uid)
    return jsonify({'applications': apps}), 200

@student_bp.route('/interviews', methods=['GET'])
@student_required
def get_my_interviews():
    uid = get_jwt_identity()
    interviews = StudentService.get_my_interviews(uid)
    return jsonify({'interviews': interviews}), 200

@student_bp.route('/history', methods=['GET'])
@student_required
def get_placement_history():
    uid = get_jwt_identity()
    history = StudentService.get_placement_history(uid)
    return jsonify({'history': history}), 200
