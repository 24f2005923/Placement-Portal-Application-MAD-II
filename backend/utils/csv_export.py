import csv
import os
from datetime import datetime, timezone

from flask import current_app


def timestamped_csv_name(prefix):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    return f'{prefix}_{stamp}.csv'


def export_path(filename):
    exports_dir = current_app.config['EXPORTS_FOLDER']
    os.makedirs(exports_dir, exist_ok=True)
    return os.path.join(exports_dir, filename)


def write_table_csv(filepath, headers, rows):
    with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_table_csv(filepath, summary_rows, headers, rows):
    with open(filepath, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for label, value in summary_rows:
            writer.writerow([label, value])
        writer.writerow([])

        table_writer = csv.DictWriter(csv_file, fieldnames=headers)
        table_writer.writeheader()
        table_writer.writerows(rows)


def export_result(filename, filepath, rows_exported, export_type, **extra):
    payload = {
        'status': 'completed',
        'filename': filename,
        'filepath': filepath,
        'rows_exported': rows_exported,
        'export_type': export_type,
    }
    payload.update(extra)
    return payload


def send_export_notification(to, export_type, filename, row_count, audience='admin'):
    from services.email_service import send_email

    panel_name = {
        'student': 'student',
        'company': 'company',
    }.get(audience, 'admin')

    subject = f'{export_type} Data Export Completed - {filename}'
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body        {{ font-family: Arial, sans-serif; color: #333; background: #f5f5f5; margin: 0; }}
        .container  {{ max-width: 560px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
        .header     {{ background: #4f46e5; color: #fff; padding: 24px 30px; }}
        .header h2  {{ margin: 0; font-size: 20px; }}
        .body       {{ padding: 24px 30px; }}
        .info-box   {{ background: #f0f0ff; border-left: 4px solid #4f46e5; padding: 14px 18px; border-radius: 4px; margin: 18px 0; }}
        .info-box p {{ margin: 4px 0; font-size: 14px; }}
        .footer     {{ background: #f9f9f9; padding: 14px 30px; font-size: 12px; color: #888; border-top: 1px solid #eee; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header"><h2>Export Completed</h2></div>
        <div class="body">
          <p>Your <strong>{export_type}</strong> data export has finished successfully.</p>
          <div class="info-box">
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Records exported:</strong> {row_count}</p>
          </div>
          <p>Log into the Placement Portal {panel_name} panel to download the file.</p>
        </div>
        <div class="footer">
          <p>Automated notification - University Placement Portal</p>
        </div>
      </div>
    </body>
    </html>
    """
    send_email(to=to, subject=subject, body_html=body_html)
