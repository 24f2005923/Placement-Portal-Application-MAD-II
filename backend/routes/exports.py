"""
exports.py — Admin CSV export API routes
─────────────────────────────────────────
Provides endpoints for admins to trigger asynchronous CSV data
exports and download the resulting files.

Endpoints:
  POST /api/admin/export/students   — queue student export job
  POST /api/admin/export/companies  — queue company export job
  GET  /api/admin/export/status/<task_id>  — check task progress
  GET  /api/admin/export/download/<filename> — download CSV file
"""

import os
import logging
from flask import Blueprint, jsonify, send_from_directory, request
from flask_jwt_extended import get_jwt

from middleware.auth_middleware import admin_required

logger = logging.getLogger(__name__)

export_bp = Blueprint('export_routes', __name__, url_prefix='/api/admin/export')


@export_bp.route('/students', methods=['POST'])
@admin_required
def trigger_student_export():
    """
    Queue an asynchronous student CSV export.

    The export runs in the background (handled by the Celery worker).
    This endpoint returns a task_id immediately — the client should
    poll /status/<task_id> to check when the export finishes.

    Request body (JSON, optional):
        notify_email — email address to notify when done
                       (defaults to the JWT token's email)

    Response:
        200 — { task_id, message, status_url }
    """
    from tasks.csv_exports import export_students_csv

    # Resolve which email to notify on completion
    jwt_claims    = get_jwt()
    payload       = request.get_json(silent=True) or {}
    notify_email  = payload.get('notify_email') or jwt_claims.get('email', '')

    # Dispatch the Celery task asynchronously (returns immediately)
    task = export_students_csv.delay(requested_by_email=notify_email)

    logger.info('Student CSV export queued: task_id=%s, notify=%s', task.id, notify_email)

    return jsonify({
        'message':    'Student export job has been queued. You will be notified when it completes.',
        'task_id':    task.id,
        'status_url': f'/api/admin/export/status/{task.id}',
    }), 202


@export_bp.route('/companies', methods=['POST'])
@admin_required
def trigger_company_export():
    """
    Queue an asynchronous company CSV export.

    Same workflow as the student export — non-blocking, poll for status.

    Request body (JSON, optional):
        notify_email — email to notify on completion

    Response:
        202 — { task_id, message, status_url }
    """
    from tasks.csv_exports import export_companies_csv

    jwt_claims   = get_jwt()
    payload      = request.get_json(silent=True) or {}
    notify_email = payload.get('notify_email') or jwt_claims.get('email', '')

    task = export_companies_csv.delay(requested_by_email=notify_email)

    logger.info('Company CSV export queued: task_id=%s, notify=%s', task.id, notify_email)

    return jsonify({
        'message':    'Company export job has been queued. You will be notified when it completes.',
        'task_id':    task.id,
        'status_url': f'/api/admin/export/status/{task.id}',
    }), 202


@export_bp.route('/status/<task_id>', methods=['GET'])
@admin_required
def get_export_status(task_id):
    """
    Check the status of a running or completed export task.

    Polls the Celery result backend (Redis) for the task state.

    Possible states:
      PENDING  — task is waiting in the queue
      STARTED  — worker has picked up the task
      SUCCESS  — task completed successfully
      FAILURE  — task failed (check 'error' field)
      RETRY    — task is being retried after an error

    Response:
        200 — { task_id, state, result | error, download_url? }
    """
    from celery_app import celery

    # AsyncResult wraps the Redis result backend lookup
    task_result = celery.AsyncResult(task_id)
    state       = task_result.state

    response = {
        'task_id': task_id,
        'state':   state,
    }

    if state == 'SUCCESS':
        result = task_result.result or {}
        response['result']  = result
        # Provide a ready-to-use download URL if the file is ready
        filename = result.get('filename')
        if filename:
            response['download_url'] = f'/api/admin/export/download/{filename}'

    elif state == 'FAILURE':
        # task_result.result holds the exception when state is FAILURE
        response['error'] = str(task_result.result)

    elif state == 'PENDING':
        response['message'] = 'Task is waiting in the queue.'

    elif state == 'STARTED':
        response['message'] = 'Task is currently running.'

    return jsonify(response), 200


@export_bp.route('/download/<filename>', methods=['GET'])
@admin_required
def download_export_file(filename):
    """
    Download a previously generated CSV export file.

    Files are stored in backend/exports/.

    Args:
        filename: The CSV filename returned by the status endpoint.

    Response:
        200 — CSV file download
        404 — File not found
    """
    from flask import current_app

    exports_dir = current_app.config['EXPORTS_FOLDER']

    # Security: only allow .csv files to prevent path traversal
    if not filename.endswith('.csv'):
        return jsonify({'error': 'Only .csv file downloads are allowed here.'}), 400

    # Check file exists before serving
    file_path = os.path.join(exports_dir, filename)
    if not os.path.isfile(file_path):
        return jsonify({'error': f'Export file not found: {filename}'}), 404

    logger.info('Admin downloading export file: %s', filename)
    return send_from_directory(exports_dir, filename, as_attachment=True)


@export_bp.route('/list', methods=['GET'])
@admin_required
def list_export_files():
    """
    List all previously generated export CSV files.

    Response:
        200 — { files: [{ filename, size_kb, created_at, download_url }] }
    """
    from flask import current_app
    from datetime import datetime

    exports_dir = current_app.config['EXPORTS_FOLDER']

    if not os.path.isdir(exports_dir):
        return jsonify({'files': []}), 200

    files_info = []
    for fname in os.listdir(exports_dir):
        if not fname.endswith('.csv'):
            continue
        fpath     = os.path.join(exports_dir, fname)
        stat      = os.stat(fpath)
        size_kb   = round(stat.st_size / 1024, 2)
        created   = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        files_info.append({
            'filename':     fname,
            'size_kb':      size_kb,
            'created_at':   created,
            'download_url': f'/api/admin/export/download/{fname}',
        })

    # Sort by newest first
    files_info.sort(key=lambda x: x['created_at'], reverse=True)

    return jsonify({'files': files_info}), 200
