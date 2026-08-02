"""
monthly_reports.py — Monthly placement report Celery task
─────────────────────────────────────────────────────────────
Generates a structured HTML placement analytics report for the requested
month/year.  All metrics are computed from live database records by
AdminService — no hardcoded values, no sample data.

Scheduled via Celery Beat (1st of every month at 06:00 UTC) or triggered
manually via POST /api/admin/reports/generate.
"""

import os
import logging
from datetime import datetime, timezone

from celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.monthly_reports.generate_monthly_report',
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def generate_monthly_report(self, target_year=None, target_month=None, requested_by_email=None):
    """
    Asynchronous task — computes placement analytics via AdminService and
    renders an HTML report saved to REPORTS_FOLDER.

    Args:
        target_year:         Optional int year  (defaults to current year).
        target_month:        Optional int month (defaults to current month).
        requested_by_email:  Optional email to notify upon completion.

    Returns:
        Dict with 'status', file paths, and headline metrics.
    """
    logger.info('=== Monthly Placement Report Task Started (task_id=%s) ===', self.request.id)

    try:
        from flask import current_app
        from services.admin_service import AdminService

        now   = datetime.now(timezone.utc)
        year  = int(target_year)  if target_year  else now.year
        month = int(target_month) if target_month else now.month

        # ── 1. Compute all metrics via the shared service layer ─────────
        analytics = AdminService.get_report_analytics()
        companies = AdminService.get_top_companies(limit=10)

        stu  = analytics['students']
        drv  = analytics['drives']
        apps = analytics['applications']
        depts = analytics['department_breakdown']

        # ── 2. Create output directory ──────────────────────────────────
        reports_base = current_app.config['REPORTS_FOLDER']
        month_str    = f"{year}-{month:02d}"
        month_dir    = os.path.join(reports_base, month_str)
        os.makedirs(month_dir, exist_ok=True)

        html_filename = 'report.html'
        html_filepath = os.path.join(month_dir, html_filename)
        rel_html_path = f"{month_str}/{html_filename}"

        # ── 3. Build HTML sections ──────────────────────────────────────
        report_title   = f"Monthly Placement Report — {datetime(year, month, 1).strftime('%B %Y')}"
        generated_time = now.strftime('%B %d, %Y %H:%M UTC')

        # Company table rows
        if companies:
            company_rows = ''.join(
                f"<tr>"
                f"<td><strong>{c['company_name']}</strong></td>"
                f"<td>{c['industry']}</td>"
                f"<td>{c['drives']}</td>"
                f"<td>{c['total_applications']}</td>"
                f"<td><span class='badge bg-success'>{c['selections']} placed</span></td>"
                f"</tr>"
                for c in companies
            )
        else:
            company_rows = "<tr><td colspan='5' class='text-center text-muted'>No approved company data available.</td></tr>"

        # Department table rows
        if depts:
            dept_rows = ''.join(
                f"<tr>"
                f"<td>{d['department']}</td>"
                f"<td>{d['total']}</td>"
                f"<td>{d['placed']}</td>"
                f"<td>{d['rate']}%</td>"
                f"</tr>"
                for d in depts
            )
        else:
            dept_rows = "<tr><td colspan='4' class='text-center text-muted'>No department data available.</td></tr>"

        # ── 4. Render full HTML ─────────────────────────────────────────
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{report_title}</title>
  <style>
    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 32px; color: #1e293b; background: #f8fafc; }}
    .card {{ background: #fff; border-radius: 12px; padding: 32px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 28px; }}
    .header {{ border-bottom: 3px solid #2563eb; padding-bottom: 20px; margin-bottom: 28px; display: flex; justify-content: space-between; align-items: flex-start; }}
    .title  {{ font-size: 24px; font-weight: 700; color: #2563eb; }}
    .sub    {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }}
    .kpi  {{ background: #f1f5f9; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; text-align: center; }}
    .kpi-val  {{ font-size: 28px; font-weight: 700; color: #2563eb; }}
    .kpi-lbl  {{ font-size: 11px; text-transform: uppercase; font-weight: 600; color: #64748b; margin-bottom: 4px; }}
    .kpi-sub  {{ font-size: 11px; color: #94a3b8; margin-top: 4px; }}
    h3  {{ font-size: 16px; font-weight: 600; color: #334155; margin: 0 0 14px 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
    th  {{ background: #f8fafc; font-weight: 600; color: #475569; }}
    .badge {{ padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
    .bg-success {{ background: #22c55e; color: #fff; }}
    .footer {{ margin-top: 36px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div>
        <div class="title">{report_title}</div>
        <div class="sub">University Placement Portal · Executive Analytics Summary</div>
      </div>
      <div style="font-size:11px; text-align:right; color:#64748b;">
        Generated: {generated_time}<br>
        Report ID: RPT-{month_str}
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-lbl">Placement Rate</div>
        <div class="kpi-val">{stu['placement_rate']}%</div>
        <div class="kpi-sub">{stu['placed']} of {stu['total']} students</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Total Drives</div>
        <div class="kpi-val">{drv['total']}</div>
        <div class="kpi-sub">{drv['open']} open · {drv['closed']} closed</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Shortlist Rate</div>
        <div class="kpi-val">{apps['shortlist_rate']}%</div>
        <div class="kpi-sub">{apps['shortlisted']} shortlisted</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Final Selections</div>
        <div class="kpi-val">{apps['selected']}</div>
        <div class="kpi-sub">{apps['selection_rate']}% conversion rate</div>
      </div>
    </div>

    <h3>Top Hiring Partners</h3>
    <table>
      <thead>
        <tr>
          <th>Company</th><th>Industry</th><th>Drives</th>
          <th>Applications</th><th>Selections</th>
        </tr>
      </thead>
      <tbody>{company_rows}</tbody>
    </table>

    <h3 style="margin-top:28px;">Department-wise Placement</h3>
    <table>
      <thead>
        <tr><th>Department</th><th>Total</th><th>Placed</th><th>Rate</th></tr>
      </thead>
      <tbody>{dept_rows}</tbody>
    </table>

    <div class="footer">
      <span>University Placement Portal · Analytics Module</span>
      <span>All data sourced from live database records</span>
    </div>
  </div>
</body>
</html>"""

        with open(html_filepath, 'w', encoding='utf-8') as fh:
            fh.write(html_content)

        logger.info('Monthly placement report written to %s', html_filepath)

        # ── 5. Optional email notification ─────────────────────────────
        if requested_by_email:
            try:
                from services.email_service import send_email
                subject   = f"Monthly Placement Report Generated — {month_str}"
                body_html = (
                    f"<p>Dear Admin,</p>"
                    f"<p>The monthly placement report for <strong>{month_str}</strong> "
                    f"has been generated successfully.</p>"
                    f"<p>Placement Rate: <strong>{stu['placement_rate']}%</strong> "
                    f"({stu['placed']} students placed)</p>"
                )
                send_email(requested_by_email, subject, body_html)
            except Exception as mail_err:
                logger.warning('Report completion email failed: %s', mail_err)

        return {
            'status':          'completed',
            'month':           month_str,
            'html_path':       rel_html_path,
            'download_url':    f'/api/admin/reports/download/{rel_html_path}',
            'placement_rate':  stu['placement_rate'],
            'placed_students': stu['placed'],
            'total_drives':    drv['total'],
        }

    except Exception as exc:
        logger.error('Monthly placement report task failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)
