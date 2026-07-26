"""
monthly_reports.py — Monthly placement report Celery task
──────────────────────────────────────────────────────────
Generates a comprehensive placement statistics report on the 1st
of every month.  The report is produced in two formats:

  1. HTML  — saved to backend/reports/YYYY-MM/report.html
  2. PDF   — saved to backend/reports/YYYY-MM/report.pdf
             (generated from the HTML using ReportLab)

The report includes:
  • Application statistics (total, by status)
  • Placement summary (placed vs. not placed students)
  • Company analytics (most active companies, industries)
  • Drive success metrics (conversion rate, selections)

Beat schedule: defined in celery_app.py — runs 1st of every month.

Retry policy:
  • Retries up to 2 times with a 10-minute delay.
"""

import io
import logging
import os
from datetime import date, datetime, timezone
from calendar import monthrange

from celery_app import celery
from models import db
from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.result import Result

logger = logging.getLogger(__name__)


@celery.task(
    name='tasks.monthly_reports.generate_monthly_report',
    bind=True,
    max_retries=2,
    default_retry_delay=600,   # retry after 10 minutes
)
def generate_monthly_report(self, target_month: str = None):
    """
    Generate the monthly placement report.

    Args:
        target_month: Optional 'YYYY-MM' string to generate a report
                      for a specific past month.  Defaults to the
                      previous calendar month.

    Returns:
        Dict with file paths and summary statistics.
    """
    logger.info('=== Monthly Report Task Started ===')

    try:
        from flask import current_app

        # ── Determine which month to report on ────────────────────
        if target_month:
            report_year, report_month = map(int, target_month.split('-'))
        else:
            today = date.today()
            # Default: report on the previous month
            if today.month == 1:
                report_month, report_year = 12, today.year - 1
            else:
                report_month, report_year = today.month - 1, today.year

        month_label = date(report_year, report_month, 1).strftime('%B %Y')
        logger.info('Generating placement report for: %s', month_label)

        # ── Collect statistics ─────────────────────────────────────
        stats = _gather_statistics(report_year, report_month)

        # ── Ensure output directories exist ───────────────────────
        reports_base = current_app.config['REPORTS_FOLDER']
        month_dir = os.path.join(reports_base, f'{report_year}-{report_month:02d}')
        os.makedirs(month_dir, exist_ok=True)

        # ── Generate HTML report ───────────────────────────────────
        html_content  = _render_html_report(month_label, stats)
        html_filename = 'placement_report.html'
        html_path     = os.path.join(month_dir, html_filename)

        with open(html_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        logger.info('HTML report saved to: %s', html_path)

        # ── Generate PDF report ────────────────────────────────────
        pdf_filename = 'placement_report.pdf'
        pdf_path     = os.path.join(month_dir, pdf_filename)
        _generate_pdf_report(month_label, stats, pdf_path)

        logger.info('PDF report saved to: %s', pdf_path)

        # ── Send summary notification ──────────────────────────────
        from services.gchat_service import send_gchat_message
        gchat_msg = (
            f"📊 *Monthly Placement Report — {month_label}*\n"
            f"Total Students: {stats['total_students']}\n"
            f"Placed Students: {stats['placed_students']}\n"
            f"Placement Rate: {stats['placement_rate']}%\n"
            f"Total Applications: {stats['total_applications']}\n"
            f"Report generated at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
        send_gchat_message(gchat_msg)

        result = {
            'status': 'completed',
            'month': month_label,
            'html_path': html_path,
            'pdf_path': pdf_path,
            'stats_summary': {
                'total_students': stats['total_students'],
                'placed_students': stats['placed_students'],
                'placement_rate': stats['placement_rate'],
                'total_applications': stats['total_applications'],
            }
        }

        logger.info('=== Monthly Report Task Done for %s ===', month_label)
        return result

    except Exception as exc:
        logger.error('Monthly report task failed: %s', exc, exc_info=True)
        raise self.retry(exc=exc)


# ── Statistics gathering ──────────────────────────────────────────

def _gather_statistics(year: int, month: int) -> dict:
    """
    Query the database and compile all statistics for the report.

    Returns a comprehensive stats dictionary used by both the HTML
    and PDF generators.
    """
    # ── Student counts ─────────────────────────────────────────────
    total_students   = db.session.query(Student).count()
    placed_students  = db.session.query(Student).filter(
        Student.placement_status == 'Placed'
    ).count()
    placement_rate = _pct(placed_students, total_students)

    # ── Application counts ─────────────────────────────────────────
    total_applications = db.session.query(Application).count()
    status_counts = {}
    for status in ['applied', 'shortlisted', 'interview', 'selected', 'rejected']:
        count = db.session.query(Application).filter(
            Application.application_status == status
        ).count()
        status_counts[status] = count

    # ── Drive statistics ───────────────────────────────────────────
    total_drives    = db.session.query(PlacementDrive).count()
    open_drives     = db.session.query(PlacementDrive).filter(
        PlacementDrive.status == 'open'
    ).count()
    closed_drives   = db.session.query(PlacementDrive).filter(
        PlacementDrive.status == 'closed'
    ).count()

    # ── Company statistics ─────────────────────────────────────────
    total_companies    = db.session.query(Company).count()
    approved_companies = db.session.query(Company).filter(
        Company.approval_status == 'approved'
    ).count()

    # Top 5 companies by number of applications received
    top_companies = _get_top_companies(limit=5)

    # Department-wise placement breakdown
    department_stats = _get_department_stats()

    # Industry breakdown
    industry_stats = _get_industry_stats()

    return {
        'total_students':       total_students,
        'placed_students':      placed_students,
        'placement_rate':       placement_rate,
        'total_applications':   total_applications,
        'status_counts':        status_counts,
        'total_drives':         total_drives,
        'open_drives':          open_drives,
        'closed_drives':        closed_drives,
        'total_companies':      total_companies,
        'approved_companies':   approved_companies,
        'top_companies':        top_companies,
        'department_stats':     department_stats,
        'industry_stats':       industry_stats,
        'interview_success_rate': _pct(status_counts.get('selected', 0), status_counts.get('interview', 0) + status_counts.get('selected', 0)),
        'generated_at':         datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }


def _get_top_companies(limit: int) -> list:
    """Return the top N companies ranked by applications received."""
    companies = db.session.query(Company).filter(
        Company.approval_status == 'approved'
    ).all()

    company_data = []
    for company in companies:
        app_count = sum(len(drive.applications) for drive in company.drives)
        if app_count > 0:
            selected = sum(
                1 for drive in company.drives
                for app in drive.applications
                if app.application_status == 'selected'
            )
            company_data.append({
                'name':        company.company_name,
                'industry':    company.industry or 'N/A',
                'drives':      len(company.drives),
                'applications': app_count,
                'selected':    selected,
            })

    # Sort by applications count descending, take top N
    company_data.sort(key=lambda x: x['applications'], reverse=True)
    return company_data[:limit]


def _get_department_stats() -> list:
    """Return placement stats grouped by student department."""
    students = db.session.query(Student).all()
    dept_map = {}

    for student in students:
        dept = student.department or 'Unknown'
        if dept not in dept_map:
            dept_map[dept] = {'total': 0, 'placed': 0}
        dept_map[dept]['total'] += 1
        if student.placement_status == 'Placed':
            dept_map[dept]['placed'] += 1

    result = []
    for dept, counts in dept_map.items():
        result.append({
            'department': dept,
            'total':      counts['total'],
            'placed':     counts['placed'],
            'rate':       _pct(counts['placed'], counts['total']),
        })

    result.sort(key=lambda x: x['total'], reverse=True)
    return result


def _get_industry_stats() -> list:
    """Return the distribution of approved companies by industry."""
    companies = db.session.query(Company).filter(
        Company.approval_status == 'approved'
    ).all()

    industry_map = {}
    for company in companies:
        industry = company.industry or 'Other'
        industry_map[industry] = industry_map.get(industry, 0) + 1

    result = [{'industry': k, 'count': v} for k, v in industry_map.items()]
    result.sort(key=lambda x: x['count'], reverse=True)
    return result


# ── HTML report generator ─────────────────────────────────────────

def _render_html_report(month_label: str, stats: dict) -> str:
    """Build the full HTML placement report as a string."""

    # Build rows for application status table
    status_rows = ''
    for status, count in stats['status_counts'].items():
        pct = _pct(count, stats['total_applications'])
        status_rows += f'<tr><td>{status.title()}</td><td>{count}</td><td>{pct}%</td></tr>'

    # Build rows for top companies table
    company_rows = ''
    for c in stats['top_companies']:
        company_rows += (
            f'<tr><td>{c["name"]}</td><td>{c["industry"]}</td>'
            f'<td>{c["drives"]}</td><td>{c["applications"]}</td>'
            f'<td>{c["selected"]}</td></tr>'
        )

    # Build rows for department table
    dept_rows = ''
    for d in stats['department_stats']:
        dept_rows += (
            f'<tr><td>{d["department"]}</td><td>{d["total"]}</td>'
            f'<td>{d["placed"]}</td><td>{d["rate"]}%</td></tr>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Placement Report — {month_label}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
    .page {{ max-width: 1000px; margin: 0 auto; background: #fff; }}
    .header {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; padding: 40px; }}
    .header h1 {{ font-size: 28px; font-weight: 700; }}
    .header p  {{ opacity: 0.85; margin-top: 6px; font-size: 14px; }}
    .content   {{ padding: 36px 40px; }}
    .section   {{ margin-bottom: 36px; }}
    .section h2 {{ font-size: 18px; font-weight: 600; color: #4f46e5; border-bottom: 2px solid #e0e0ff; padding-bottom: 8px; margin-bottom: 18px; }}
    .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
    .metric {{ background: #f8f7ff; border: 1px solid #e0e0ff; border-radius: 10px; padding: 20px; text-align: center; }}
    .metric .value {{ font-size: 32px; font-weight: 700; color: #4f46e5; }}
    .metric .label {{ font-size: 13px; color: #666; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th {{ background: #4f46e5; color: #fff; padding: 10px 14px; text-align: left; font-weight: 600; }}
    td {{ padding: 10px 14px; border-bottom: 1px solid #eee; }}
    tr:hover td {{ background: #f8f7ff; }}
    .footer {{ background: #f9f9f9; padding: 20px 40px; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
  </style>
</head>
<body>
<div class="page">
  <div class="header">
    <h1>📊 Monthly Placement Report</h1>
    <p>{month_label} &nbsp;|&nbsp; Generated: {stats['generated_at']}</p>
  </div>

  <div class="content">

    <!-- Key Metrics -->
    <div class="section">
      <h2>Key Metrics</h2>
      <div class="metrics-grid">
        <div class="metric"><div class="value">{stats['total_students']}</div><div class="label">Total Students</div></div>
        <div class="metric"><div class="value">{stats['placed_students']}</div><div class="label">Placed Students</div></div>
        <div class="metric"><div class="value">{stats['placement_rate']}%</div><div class="label">Placement Rate</div></div>
        <div class="metric"><div class="value">{stats['total_applications']}</div><div class="label">Total Applications</div></div>
      </div>
    </div>

    <!-- Drive Summary -->
    <div class="section">
      <h2>Drive Summary</h2>
      <div class="metrics-grid">
        <div class="metric"><div class="value">{stats['total_drives']}</div><div class="label">Total Drives</div></div>
        <div class="metric"><div class="value">{stats['open_drives']}</div><div class="label">Open Drives</div></div>
        <div class="metric"><div class="value">{stats['closed_drives']}</div><div class="label">Closed Drives</div></div>
        <div class="metric"><div class="value">{stats['interview_success_rate']}%</div><div class="label">Interview Success</div></div>
      </div>
    </div>

    <!-- Application Pipeline -->
    <div class="section">
      <h2>Application Pipeline</h2>
      <table>
        <thead><tr><th>Status</th><th>Count</th><th>% of Total</th></tr></thead>
        <tbody>{status_rows or '<tr><td colspan="3">No applications recorded.</td></tr>'}</tbody>
      </table>
    </div>

    <!-- Top Companies -->
    <div class="section">
      <h2>Top Companies by Applications</h2>
      <table>
        <thead><tr><th>Company</th><th>Industry</th><th>Drives</th><th>Applications</th><th>Selected</th></tr></thead>
        <tbody>{company_rows or '<tr><td colspan="5">No company data available.</td></tr>'}</tbody>
      </table>
    </div>

    <!-- Department-wise Placement -->
    <div class="section">
      <h2>Department-wise Placement</h2>
      <table>
        <thead><tr><th>Department</th><th>Total Students</th><th>Placed</th><th>Rate</th></tr></thead>
        <tbody>{dept_rows or '<tr><td colspan="4">No department data available.</td></tr>'}</tbody>
      </table>
    </div>

  </div>

  <div class="footer">
    <p>This is an auto-generated report from the University Placement Portal.
       Data reflects cumulative records as of the report generation date.</p>
  </div>
</div>
</body>
</html>"""


# ── PDF report generator ──────────────────────────────────────────

def _generate_pdf_report(month_label: str, stats: dict, output_path: str):
    """
    Generate a PDF placement report using ReportLab.

    ReportLab is a pure-Python library — no system binaries required.
    The PDF mirrors the key sections of the HTML report.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable
        )

        doc    = SimpleDocTemplate(output_path, pagesize=A4,
                                   leftMargin=2*cm, rightMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []

        # ── Title ──────────────────────────────────────────────────
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            fontSize=22,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=4,
        )
        story.append(Paragraph(f'Placement Report — {month_label}', title_style))
        story.append(Paragraph(f'Generated: {stats["generated_at"]}', styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width='100%', color=colors.HexColor('#4f46e5')))
        story.append(Spacer(1, 0.5*cm))

        # ── Section helper ─────────────────────────────────────────
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4f46e5'),
            spaceBefore=16,
            spaceAfter=8,
        )

        table_header_bg = colors.HexColor('#4f46e5')
        table_alt_bg    = colors.HexColor('#f8f7ff')

        def make_table(headers, rows, col_widths=None):
            data = [headers] + (rows if rows else [['No data available'] + [''] * (len(headers)-1)])
            tbl  = Table(data, colWidths=col_widths)
            tbl.setStyle(TableStyle([
                ('BACKGROUND',   (0, 0), (-1, 0), table_header_bg),
                ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
                ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE',     (0, 0), (-1, 0), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, table_alt_bg]),
                ('FONTSIZE',     (0, 1), (-1, -1), 9),
                ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING',      (0, 0), (-1, -1), 6),
            ]))
            return tbl

        # ── Key Metrics ────────────────────────────────────────────
        story.append(Paragraph('Key Metrics', section_style))
        metrics_rows = [[
            str(stats['total_students']), str(stats['placed_students']),
            f"{stats['placement_rate']}%", str(stats['total_applications'])
        ]]
        story.append(make_table(
            ['Total Students', 'Placed', 'Placement Rate', 'Applications'],
            metrics_rows
        ))
        story.append(Spacer(1, 0.4*cm))

        # ── Application pipeline ───────────────────────────────────
        story.append(Paragraph('Application Pipeline', section_style))
        pipe_rows = [
            [status.title(), str(count), f"{_pct(count, stats['total_applications'])}%"]
            for status, count in stats['status_counts'].items()
        ]
        story.append(make_table(['Status', 'Count', '% of Total'], pipe_rows))
        story.append(Spacer(1, 0.4*cm))

        # ── Top companies ──────────────────────────────────────────
        story.append(Paragraph('Top Companies by Applications', section_style))
        comp_rows = [
            [c['name'], c['industry'], str(c['drives']), str(c['applications']), str(c['selected'])]
            for c in stats['top_companies']
        ]
        story.append(make_table(
            ['Company', 'Industry', 'Drives', 'Applications', 'Selected'], comp_rows
        ))
        story.append(Spacer(1, 0.4*cm))

        # ── Department stats ───────────────────────────────────────
        story.append(Paragraph('Department-wise Placement', section_style))
        dept_rows = [
            [d['department'], str(d['total']), str(d['placed']), f"{d['rate']}%"]
            for d in stats['department_stats']
        ]
        story.append(make_table(
            ['Department', 'Total Students', 'Placed', 'Rate'], dept_rows
        ))

        doc.build(story)
        logger.info('PDF report generated: %s', output_path)

    except ImportError:
        logger.error('ReportLab is not installed. Run: pip install reportlab')
    except Exception as exc:
        logger.error('PDF generation failed: %s', exc, exc_info=True)


# ── Utility ───────────────────────────────────────────────────────

def _pct(part: int, total: int) -> float:
    """Calculate percentage rounded to one decimal place."""
    return round((part / total) * 100, 1) if total > 0 else 0.0
