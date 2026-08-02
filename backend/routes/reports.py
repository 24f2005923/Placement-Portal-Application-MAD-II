"""
reports.py — Admin placement report API routes
─────────────────────────────────────────────────
Provides endpoints for live analytics, queuing/checking report generation
tasks, listing available reports, and downloading them.

All analytics values are computed from live database records by
AdminService — no hardcoded, mocked, or seeded data exists here.
"""

import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from middleware.auth_middleware import admin_required
from services.admin_service import AdminService
from cache.decorators import cache_response

report_bp = Blueprint('report_routes', __name__, url_prefix='/api/admin/reports')


@report_bp.route('/analytics', methods=['GET'])
@admin_required
@cache_response(lambda: 'reports:analytics', ttl=300)
def get_placement_analytics():
    """
    Return live placement analytics computed from the database.
    Includes student placement rates, drive counts, application funnel
    percentages, and department-wise breakdowns.  Returns zeros when
    no records exist — never returns fabricated values.
    """
    analytics = AdminService.get_report_analytics()
    return jsonify({'analytics': analytics}), 200


@report_bp.route('/companies/top', methods=['GET'])
@admin_required
@cache_response(lambda: 'reports:companies:top', ttl=300)
def get_top_hiring_companies():
    """
    Return approved companies ranked by confirmed student selections.
    Uses a single aggregated DB query — no per-row sub-queries.
    Returns an empty list when no approved company data exists.
    """
    limit = min(int(request.args.get('limit', 10)), 50)
    companies = AdminService.get_top_companies(limit=limit)
    return jsonify({'companies': companies}), 200


@report_bp.route('/generate', methods=['POST'])
@admin_required
def generate_report():
    """Queue asynchronous monthly placement report generation task."""
    from tasks.monthly_reports import generate_monthly_report

    payload = request.get_json() or {}
    year  = payload.get('year')
    month = payload.get('month')

    task = generate_monthly_report.delay(target_year=year, target_month=month)

    return jsonify({
        'message': 'Monthly placement report generation task queued',
        'task_id': task.id,
        'status_url': f'/api/admin/reports/status/{task.id}'
    }), 202


@report_bp.route('/status/<task_id>', methods=['GET'])
@admin_required
def get_report_status(task_id):
    """Check status of an asynchronous report generation task."""
    from celery_app import celery

    res = celery.AsyncResult(task_id)
    if res.state == 'PENDING':
        return jsonify({'state': 'PENDING', 'status': 'Task queued / processing...'}), 200
    elif res.state == 'SUCCESS':
        return jsonify({'state': 'SUCCESS', 'result': res.result}), 200
    elif res.state == 'FAILURE':
        return jsonify({'state': 'FAILURE', 'error': str(res.result)}), 500
    else:
        return jsonify({'state': res.state}), 200


@report_bp.route('/list', methods=['GET'])
@admin_required
def list_reports():
    """List all available generated monthly reports in REPORTS_FOLDER."""
    reports_base = current_app.config['REPORTS_FOLDER']
    if not os.path.exists(reports_base):
        return jsonify({'reports': []}), 200

    reports = []
    for month_dir in sorted(os.listdir(reports_base), reverse=True):
        full_dir = os.path.join(reports_base, month_dir)
        if os.path.isdir(full_dir):
            html_file = os.path.join(full_dir, 'report.html')
            if os.path.exists(html_file):
                reports.append({
                    'month': month_dir,
                    'html_filename': 'report.html',
                    'rel_path': f"{month_dir}/report.html",
                    'download_url': f"/api/admin/reports/download/{month_dir}/report.html"
                })

    return jsonify({'reports': reports}), 200


@report_bp.route('/download/<path:fname>', methods=['GET'])
@admin_required
def download_report(fname):
    """Download or view a generated monthly report file from REPORTS_FOLDER."""
    reports_base = current_app.config['REPORTS_FOLDER']
    return send_from_directory(reports_base, fname)
