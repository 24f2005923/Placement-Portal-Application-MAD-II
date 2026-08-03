from datetime import datetime, timezone

from flask import Blueprint
from flask_jwt_extended import get_jwt_identity

from middleware.auth_middleware import admin_required
from models import db
from models.user import User
from services.admin_service import AdminService
from utils.request_helpers import json_payload
from utils.responses import success_response
from utils.task_runner import async_result_response, dispatch_task, task_dispatch_response

report_bp = Blueprint('report_routes', __name__, url_prefix='/api/admin/reports')


@report_bp.route('/monthly-activity', methods=['GET'])
@admin_required
def get_monthly_activity_report():
    """Return monthly activity metrics for the selected month and year."""
    from flask import request

    now = datetime.now(timezone.utc)
    year = request.args.get('year', now.year)
    month = request.args.get('month', now.month)

    report = AdminService.get_monthly_activity_report(year, month)
    return success_response({'report': report})


@report_bp.route('/generate', methods=['POST'])
@admin_required
def generate_report():
    """Queue CSV generation for the selected monthly activity report."""
    from tasks.monthly_reports import generate_monthly_report

    payload = json_payload()
    year = payload.get('year')
    month = payload.get('month')
    admin_email = payload.get('notify_email') or _current_admin_email()

    dispatched = dispatch_task(
        generate_monthly_report,
        target_year=year,
        target_month=month,
        requested_by_email=admin_email,
    )
    return task_dispatch_response(
        dispatched,
        queued_message='Monthly placement activity report generation queued.',
        completed_message='Monthly placement activity report generated.',
        status_url_prefix='/api/admin/reports/status',
        download_url_builder=_report_download_url,
    )


@report_bp.route('/status/<task_id>', methods=['GET'])
@admin_required
def get_report_status(task_id):
    """Check the status of a monthly activity report task."""
    from celery_app import celery

    task_result = celery.AsyncResult(task_id)
    return async_result_response(
        task_id,
        task_result,
        download_url_builder=_report_download_url,
        pending_message='Monthly activity report task queued / processing...',
    )


def _current_admin_email():
    user_id = get_jwt_identity()
    if not user_id:
        return None

    user = db.session.query(User).filter(User.id == int(user_id)).first()
    return user.email if user else None


def _report_download_url(result):
    filename = (result or {}).get('filename')
    return f'/api/admin/export/download/{filename}' if filename else None
