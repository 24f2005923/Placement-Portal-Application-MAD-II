"""
reports.py — Admin placement report API routes
────────────────────────────────────────────────
Provides endpoints for admins to trigger the monthly placement
report generation task and download the output files.

Endpoints:
  POST /api/admin/reports/generate              — queue report generation
  GET  /api/admin/reports/status/<task_id>      — check task progress
  GET  /api/admin/reports/download/<path:fname> — download HTML or PDF
  GET  /api/admin/reports/list                  — list available reports
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, send_from_directory

from middleware.auth_middleware import admin_required

logger = logging.getLogger(__name__)

report_bp = Blueprint('report_routes', __name__, url_prefix='/api/admin/reports')


@report_bp.route('/generate', methods=['POST'])
@admin_required
def trigger_report_generation():
    """
    Queue an asynchronous monthly placement report generation task.

    Request body (JSON, optional):
        month — Target month in 'YYYY-MM' format.
                Defaults to the previous calendar month.

    Response:
        202 — { task_id, message, status_url, month }
    """
    from tasks.monthly_reports import generate_monthly_report

    payload      = request.get_json(silent=True) or {}
    target_month = payload.get('month')    # e.g. "2026-06"

    # Validate the month format if provided
    if target_month:
        try:
            datetime.strptime(target_month, '%Y-%m')
        except ValueError:
            return jsonify({'error': "Invalid month format. Use 'YYYY-MM' (e.g. '2026-06')"}), 400

    task = generate_monthly_report.delay(target_month=target_month)

    logger.info('Report generation queued: task_id=%s, month=%s', task.id, target_month or 'previous')

    return jsonify({
        'message':    'Report generation job has been queued.',
        'task_id':    task.id,
        'month':      target_month or 'previous month',
        'status_url': f'/api/admin/reports/status/{task.id}',
    }), 202


@report_bp.route('/status/<task_id>', methods=['GET'])
@admin_required
def get_report_status(task_id):
    """
    Check the status of a report generation task.

    Response:
        200 — { task_id, state, result | error, download_urls? }
    """
    from celery_app import celery

    task_result = celery.AsyncResult(task_id)
    state       = task_result.state

    response = {
        'task_id': task_id,
        'state':   state,
    }

    if state == 'SUCCESS':
        result = task_result.result or {}
        response['result'] = result

        # Provide download links for both HTML and PDF
        month_label = result.get('month', '')
        response['download_urls'] = {
            'html': f"/api/admin/reports/download/{result.get('html_path', '')}",
            'pdf':  f"/api/admin/reports/download/{result.get('pdf_path', '')}",
        }

    elif state == 'FAILURE':
        response['error'] = str(task_result.result)

    return jsonify(response), 200


@report_bp.route('/download/<path:filepath>', methods=['GET'])
@admin_required
def download_report_file(filepath):
    """
    Download a generated report file (HTML or PDF).

    The filepath is the absolute path returned in the task result.
    For security, only files within backend/reports/ are served.

    Response:
        200 — File download
        403 — Attempt to access outside reports directory
        404 — File not found
    """
    from flask import current_app

    reports_base = current_app.config['REPORTS_FOLDER']

    # Security: resolve the absolute path and verify it's in reports dir
    abs_path = os.path.abspath(filepath)
    if not abs_path.startswith(os.path.abspath(reports_base)):
        logger.warning('Report download blocked — path traversal attempt: %s', filepath)
        return jsonify({'error': 'Access denied.'}), 403

    if not os.path.isfile(abs_path):
        return jsonify({'error': 'Report file not found.'}), 404

    directory = os.path.dirname(abs_path)
    filename  = os.path.basename(abs_path)

    logger.info('Admin downloading report: %s', filename)
    return send_from_directory(directory, filename, as_attachment=True)


@report_bp.route('/list', methods=['GET'])
@admin_required
def list_reports():
    """
    List all generated monthly reports, grouped by month.

    Response:
        200 — { reports: [{ month, html, pdf, created_at }] }
    """
    from flask import current_app

    reports_base = current_app.config['REPORTS_FOLDER']

    if not os.path.isdir(reports_base):
        return jsonify({'reports': []}), 200

    reports = []
    for month_folder in sorted(os.listdir(reports_base), reverse=True):
        month_path = os.path.join(reports_base, month_folder)
        if not os.path.isdir(month_path):
            continue

        html_path = os.path.join(month_path, 'placement_report.html')
        pdf_path  = os.path.join(month_path, 'placement_report.pdf')

        html_exists = os.path.isfile(html_path)
        pdf_exists  = os.path.isfile(pdf_path)

        if not html_exists and not pdf_exists:
            continue

        created_at = ''
        if html_exists:
            ts = os.path.getmtime(html_path)
            created_at = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

        reports.append({
            'month':      month_folder,
            'html_url':   f'/api/admin/reports/download/{html_path}' if html_exists else None,
            'pdf_url':    f'/api/admin/reports/download/{pdf_path}' if pdf_exists else None,
            'created_at': created_at,
        })

    return jsonify({'reports': reports}), 200
