import datetime

class EmailTemplateBuilder:
    """Centralized HTML template builder for standard emails."""

    @staticmethod
    def get_base_template(title, body_content):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{ font-family: Arial, sans-serif; color: #333; background: #f5f5f5; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 30px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .header {{ background: #4f46e5; color: #fff; padding: 28px 32px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 22px; }}
            .body {{ padding: 28px 32px; }}
            .body p {{ line-height: 1.6; }}
            .button {{ display: inline-block; background: #4f46e5; color: #ffffff !important; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 15px; }}
            .footer {{ background: #f9f9f9; padding: 16px 32px; font-size: 12px; color: #888; border-top: 1px solid #eee; text-align: center; }}
            .details-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .status-banner {{ font-size: 20px; font-weight: bold; margin: 16px 0; padding: 12px; background-color: #eef2ff; color: #0d6efd; border-radius: 6px; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>{title}</h1>
            </div>
            <div class="body">
              {body_content}
            </div>
            <div class="footer">
              <p>This is an automated notification from University Placement Portal. Please do not reply.</p>
            </div>
          </div>
        </body>
        </html>
        """

    @staticmethod
    def build_status_update_email(student_name, drive_title, company_name, status, details=None):
        status_display = status.capitalize()
        details_html = f"<div class='details-box'><strong>Details:</strong> {details}</div>" if details else ""
        
        body = f"""
        <p>Dear <strong>{student_name}</strong>,</p>
        <p>Your application status for <strong>{drive_title}</strong> at <strong>{company_name}</strong> has been updated to:</p>
        <div class="status-banner">
          {status_display}
        </div>
        {details_html}
        <p>Please log in to your student placement dashboard for further information.</p>
        """
        return EmailTemplateBuilder.get_base_template("Application Status Update", body)

    @staticmethod
    def build_interview_reminder_email(student_name, drive_title, company_name, round_name, date_str, time_str, mode_str, link_str):
        body = f"""
        <p>Dear <strong>{student_name}</strong>,</p>
        <p>This is a reminder for your upcoming interview for the <strong>{drive_title}</strong> role at <strong>{company_name}</strong>.</p>
        <div class="details-box">
            <p style="margin: 5px 0;"><strong>Round:</strong> {round_name}</p>
            <p style="margin: 5px 0;"><strong>Date:</strong> {date_str}</p>
            <p style="margin: 5px 0;"><strong>Time:</strong> {time_str}</p>
            <p style="margin: 5px 0;"><strong>Mode:</strong> {mode_str}</p>
            <p style="margin: 5px 0;"><strong>Link / Location:</strong> {link_str}</p>
        </div>
        <p>Please ensure you are prepared and join on time. Best of luck!</p>
        """
        return EmailTemplateBuilder.get_base_template("Interview Reminder", body)

    @staticmethod
    def build_weekly_login_reminder():
        body = """
        <p>Hello Students!</p>
        <p>This is a friendly reminder to log in to the Placement Portal and check your dashboard. New placement drives or announcements may have been posted!</p>
        <p>Keeping your profile updated and checking regularly ensures you don't miss any deadlines.</p>
        <center>
          <a href="http://localhost:5173/login" class="button">Go to Placement Portal</a>
        </center>
        """
        return EmailTemplateBuilder.get_base_template("Reminder to Login", body)

    @staticmethod
    def build_offer_letter(student_name, reg_num, dept, company_name, job_role, package_val, applied_date, app_id):
        current_date = datetime.datetime.now().strftime('%B %d, %Y')
        html_doc = f"""<!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Placement Offer Letter - {company_name}</title>
          <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin: 40px; color: #222; background-color: #fff; line-height: 1.6; }}
            .header {{ border-bottom: 3px solid #0d6efd; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
            .company-name {{ font-size: 26px; font-weight: bold; color: #0d6efd; }}
            .doc-title {{ font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #555; text-align: right; }}
            .meta-table {{ width: 100%; margin-bottom: 30px; border-collapse: collapse; }}
            .meta-table td {{ padding: 6px 0; font-size: 14px; }}
            .content {{ font-size: 15px; margin-bottom: 40px; }}
            .highlight {{ background-color: #eef2ff; border-left: 4px solid #0d6efd; padding: 15px; margin: 20px 0; border-radius: 4px; }}
            .footer {{ border-top: 1px solid #ddd; padding-top: 20px; margin-top: 50px; font-size: 12px; color: #777; display: flex; justify-content: space-between; }}
            .signature {{ margin-top: 50px; display: flex; justify-content: space-between; }}
            .sig-block {{ text-align: center; width: 220px; border-top: 1px solid #333; padding-top: 8px; font-size: 14px; font-weight: bold; }}
          </style>
        </head>
        <body>
          <div class="header">
            <div>
              <div class="company-name">{company_name}</div>
              <div style="font-size: 13px; color: #555; margin-top: 4px;">In Association with University Placement Cell</div>
            </div>
            <div class="doc-title">OFFICIAL PLACEMENT CONFIRMATION</div>
          </div>

          <table class="meta-table">
            <tr><td><strong>Date:</strong> {current_date}</td><td style="text-align: right;"><strong>Ref No:</strong> OFF-{app_id:06d}</td></tr>
            <tr><td><strong>Candidate Name:</strong> {student_name}</td><td style="text-align: right;"><strong>Register No:</strong> {reg_num}</td></tr>
            <tr><td><strong>Department:</strong> {dept}</td><td style="text-align: right;"><strong>Applied Date:</strong> {applied_date}</td></tr>
          </table>

          <div class="content">
            <p>Dear <strong>{student_name}</strong>,</p>
            <p>We are pleased to inform you that following your evaluation during the campus placement drive conducted by the University Placement Cell, <strong>{company_name}</strong> is delighted to offer you employment for the position of <strong>{job_role}</strong>.</p>
            
            <div class="highlight">
              <strong>Offer Summary Details:</strong><br/>
              • <strong>Designation:</strong> {job_role}<br/>
              • <strong>Compensation Package:</strong> {package_val}<br/>
              • <strong>Placement Status:</strong> Confirmed & Placed<br/>
              • <strong>Organization:</strong> {company_name}
            </div>

            <p>Your technical proficiency, problem-solving capabilities, and academic accomplishments impressed our selection panel. Official joining instructions and onboarding documentation will be delivered to your registered email address.</p>
            
            <p>We congratulate you on this milestone and look forward to your contributions at <strong>{company_name}</strong>.</p>
          </div>

          <div class="signature">
            <div class="sig-block">Head of Campus Recruitment<br/><span style="font-weight: normal; font-size: 12px;">{company_name}</span></div>
            <div class="sig-block">Director of Placements<br/><span style="font-weight: normal; font-size: 12px;">University Placement Cell</span></div>
          </div>

          <div class="footer">
            <span>Issued via University Placement Portal</span>
            <span>Document Verification Code: VERIFIED-OFFER-{app_id}</span>
          </div>
        </body>
        </html>"""
        clean_company = "".join(c for c in company_name if c.isalnum() or c == '_')
        clean_student = "".join(c for c in student_name if c.isalnum() or c == '_')
        return html_doc, f"Offer_Letter_{clean_company}_{clean_student}.html"
