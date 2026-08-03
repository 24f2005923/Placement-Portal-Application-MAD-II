# MailHog Setup on a Fresh Computer

This guide is for someone who downloads this project from GitHub on a new
machine and wants all placement portal emails to appear in a local browser
inbox instead of being sent to real email addresses.

The project now starts without committed dummy data:

- `backend/database/placement.db` is generated automatically on first backend startup.
- Database tables are created automatically by `db.create_all()` in `backend/app.py`.
- No demo students, companies, drives, applications, exports, reports, or resumes are loaded.
- The only optional startup record is the initial admin account controlled by `.env`.

## What MailHog Does

MailHog is a local email testing server.

- SMTP server: `localhost:1025`
- Browser inbox: `http://localhost:8025`
- No email leaves your computer.
- Any recipient address used by the app is captured only inside MailHog.

## Email Workflows Captured

MailHog captures email from these features:

| Feature | When email is generated |
|---|---|
| Application status update | A company shortlists, rejects, or selects a student |
| Interview scheduled | A company schedules an interview |
| Interview reminder | Manual reminder or scheduled Celery task |
| Drive deadline reminder | Scheduled Celery task before a deadline |
| Weekly login reminder | Scheduled Celery task |
| CSV export complete | Admin triggers an export |
| Monthly report generated | Admin triggers or schedules a report |

Emails are generated only from real records created in the local database.
Since no dummy data is committed, create students, companies, drives, and
applications through the UI before testing those workflows.

## Required Software

Install these before running the project:

- Python 3.10 or later
- Node.js 18 or later
- Redis-compatible server for Celery jobs
- Git

Redis options:

- Windows: install Memurai from `https://www.memurai.com/`
- macOS: `brew install redis`
- Linux: `sudo apt install redis-server`

## 1. Clone the Project

```bash
git clone <your-github-repo-url>
cd Placement-Portal-Application-MAD-II
```

## 2. Install Backend Dependencies

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Create the Backend `.env`

From the `backend` folder:

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

The MailHog settings are already configured:

```env
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_SENDER=noreply@placement-portal.local
```

The first-run database settings are also included:

```env
SEED_ADMIN=true
DEFAULT_ADMIN_EMAIL=admin@admin.com
DEFAULT_ADMIN_PASSWORD=password
DEFAULT_ADMIN_NAME=Portal Admin
```

Set `SEED_ADMIN=false` if you want the database to be completely empty on
first startup. With `SEED_ADMIN=true`, only one admin account is created.
No other dummy data is generated.

## 4. Start MailHog

### Windows

This repository includes `backend/MailHog.exe`.

Open a terminal:

```powershell
cd backend
.\MailHog.exe
```

Expected ports:

```text
HTTP: 8025
SMTP: 1025
```

Keep this terminal open.

### macOS

```bash
brew install mailhog
mailhog
```

### Linux or Manual Download

Download a binary from:

```text
https://github.com/mailhog/MailHog/releases
```

Then run the downloaded binary from a terminal.

## 5. Start Redis

Windows with Memurai:

```powershell
memurai
```

macOS:

```bash
brew services start redis
```

Linux:

```bash
sudo service redis-server start
```

Redis is required for Celery background jobs. Immediate emails from normal API
actions can work without Celery, but scheduled reminders, exports, and reports
need Redis plus a Celery worker.

## 6. Start the Flask Backend

Open a new terminal:

```bash
cd backend
python app.py
```

On first startup, Flask automatically creates:

```text
backend/database/placement.db
backend/uploads/resumes/
backend/exports/
backend/reports/
```

It also creates all database tables. If `SEED_ADMIN=true`, it creates the
admin login from `.env`.

Backend URL:

```text
http://localhost:5000
```

Health check:

```text
http://localhost:5000/api/health
```

## 7. Start the Vue Frontend

Open a new terminal from the project root:

```bash
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## 8. Start Celery Worker

Open a new terminal:

```bash
cd backend
python run_worker.py
```

Keep it running for background email jobs.

## 9. Start Celery Beat

Open a new terminal:

```bash
cd backend
python run_beat.py
```

Keep it running for scheduled jobs.

## 10. Open the MailHog Inbox

Open this URL in your browser:

```text
http://localhost:8025
```

There is no login. Every email sent by the app appears in this inbox.

## 11. Test Email Capture

Because no dummy data is loaded, create test records through the app:

1. Log in as admin using the `.env` admin credentials.
2. Register or approve a company.
3. Register or approve a student.
4. Create a placement drive from the company side.
5. Apply to the drive from the student side.
6. Shortlist, reject, select, or schedule an interview.
7. Open `http://localhost:8025`.

The generated email should appear in MailHog.

## Manual Celery Email Tests

Run these from the `backend` folder while Redis and Celery Worker are running:

```bash
celery -A celery_app call tasks.interview_reminders.send_interview_reminders
celery -A celery_app call tasks.drive_reminders.send_drive_deadline_reminders
celery -A celery_app call tasks.announcements.weekly_login_reminder
```

These tasks send emails only if matching records exist in your local database.

## Port Reference

| Port | Service |
|---|---|
| 1025 | MailHog SMTP |
| 8025 | MailHog browser inbox |
| 5000 | Flask API |
| 5173 | Vue frontend |
| 6379 | Redis |

## Troubleshooting

### MailHog inbox is empty

Check these items:

- MailHog is running.
- Browser opens `http://localhost:8025`.
- `backend/.env` has `MAIL_SERVER=localhost`.
- `backend/.env` has `MAIL_PORT=1025`.
- Flask was restarted after editing `.env`.
- The app action actually generated an email.
- The local database has real records for the workflow being tested.

### SMTP login error

MailHog does not need authentication. Keep these values from `.env.example`:

```env
MAIL_USE_TLS=false
MAIL_USERNAME=
MAIL_PASSWORD=
```

The app only calls SMTP login when `MAIL_USERNAME` is present, so leaving it
blank prevents unnecessary authentication against MailHog.

### Port 1025 is already used

Windows:

```powershell
netstat -ano | findstr :1025
```

Run MailHog on another SMTP port:

```powershell
.\MailHog.exe -smtp-bind-addr 0.0.0.0:2025
```

Then update `backend/.env`:

```env
MAIL_PORT=2025
```

Restart Flask after changing `.env`.

### Database did not reset

The database is local runtime state. To start again from a blank local database:

1. Stop Flask, Celery Worker, and Celery Beat.
2. Delete `backend/database/placement.db`.
3. Start `python app.py` again.

The file and tables are generated automatically.

### Celery jobs do not run

Confirm all three are running:

- Redis
- `python run_worker.py`
- `python run_beat.py`

Scheduled emails will not run from Flask alone.

## Production Email

For production, do not use MailHog. Replace the MailHog settings in
`backend/.env` with a real SMTP provider:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_SENDER=noreply@your-domain.com
```

For Gmail, use an app password, not your normal Gmail password.

## Quick Windows Startup

Use separate terminals:

```powershell
# Terminal 1
cd backend
.\MailHog.exe

# Terminal 2
cd backend
python app.py

# Terminal 3
npm run dev

# Terminal 4
cd backend
python run_worker.py

# Terminal 5
cd backend
python run_beat.py
```

Then open:

```text
http://localhost:8025
```
