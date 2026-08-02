# Background Jobs & Redis Caching — Developer Guide

This document explains how the asynchronous background job system and
Redis caching layer work in the Placement Portal backend.

---

## Architecture Overview

```
┌─────────────────┐       ┌──────────────┐       ┌───────────────────┐
│  Flask API      │──────▶│  Redis       │◀──────│  Celery Worker    │
│  (app.py)       │ tasks │  (broker)    │ jobs  │  (run_worker.py)  │
│                 │       │              │       │                   │
│  /api/admin/    │       │  Redis       │       │  tasks/           │
│  export/...     │──────▶│  (cache)     │       │  interview_*      │
│  reports/...    │       │              │       │  monthly_*        │
└─────────────────┘       └──────────────┘       │  csv_exports      │
                                ▲                └───────────────────┘
                                │                        ▲
                          ┌─────┴──────┐         ┌──────┴──────┐
                          │ Celery Beat │         │  Scheduled  │
                          │(run_beat.py)│         │  Tasks      │
                          └────────────┘         └─────────────┘
```

---

## Prerequisites & Local Setup

Follow these steps **in order** to run the full background job stack locally.

---

### Step 1 — Install Python dependencies

From the `backend/` directory:
```bash
pip install -r requirements.txt
```

Key packages installed:
| Package | Purpose |
|---|---|
| `python-dotenv` | Load `.env` into `os.environ` |
| `celery[redis]` | Async task queue |
| `redis` | Redis Python client |
| `reportlab` | PDF report generation |
| `flower` | Celery monitoring dashboard |

---

### Step 2 — Create your `.env` file

If `backend/.env` does not exist, copy the example and fill in values:
```bash
cd backend
copy .env.example .env    # Windows
# or
cp .env.example .env       # macOS/Linux
```

The `.env` file is loaded automatically by `config.py` via `python-dotenv`.
Every value in `.env` overrides the hardcoded defaults, **but real system
environment variables always take precedence** (`override=False`).

**Minimum required values for local development:**
```env
SECRET_KEY=any-random-string
JWT_SECRET_KEY=any-random-jwt-string
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# MailHog (see Step 4)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
MAIL_USERNAME=dev@placement-portal.local
MAIL_PASSWORD=mailhog
MAIL_SENDER=noreply@placement-portal.local
```

> **Why MAIL_USERNAME must not be empty:** `email_service.py` checks whether
> `MAIL_USERNAME` is set. An empty value activates console mode (emails printed
> to the log). Any non-empty string activates real SMTP delivery. MailHog
> accepts any username/password, so the values above are intentional.

---

### Step 3 — Install & start Redis

**Windows — Memurai (native Redis port, recommended):**
1. Download from https://www.memurai.com/ and run the installer.
2. Memurai starts automatically as a Windows service on port 6379.

**Windows — WSL (Ubuntu subsystem):**
```bash
# Inside your WSL terminal:
sudo apt-get install redis-server
redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo service redis-server start
```

Verify Redis is running:
```bash
redis-cli ping   # Expected output: PONG
```

---

### Step 4 — Install & start MailHog

MailHog is a local SMTP server with a web inbox. Emails sent through it
never leave your machine.

**Download:** https://github.com/mailhog/MailHog/releases

Pick the binary for your OS:
- Windows: `MailHog_windows_amd64.exe`
- macOS:   `MailHog_darwin_amd64`
- Linux:   `MailHog_linux_amd64`

**Start MailHog:**
```bash
# Windows PowerShell (from the folder containing the binary):
.\MailHog_windows_amd64.exe

# macOS/Linux:
chmod +x ./MailHog_linux_amd64
./MailHog_linux_amd64
```

MailHog listens on:
- **SMTP:** `localhost:1025` — receives emails from the application
- **Web UI:** http://localhost:8025 — view the inbox in your browser

> MailHog requires no username or password. Any SMTP credentials you
> provide are accepted silently.

---

### Step 5 — Start services in order

Open **four separate terminals**, all from the `backend/` directory:

**Terminal 1 — Flask API:**
```bash
python app.py
```

**Terminal 2 — Celery Worker:**
```bash
python run_worker.py
```

**Terminal 3 — Celery Beat (scheduler):**
```bash
python run_beat.py
```

**Terminal 4 — MailHog:**
```bash
.\MailHog_windows_amd64.exe
```

---

### Step 6 — Verify the stack

| Check | Command / URL | Expected Result |
|---|---|---|
| Redis running | `redis-cli ping` | `PONG` |
| Flask API | `http://localhost:5000/api/health` | `{"status": "ok"}` |
| MailHog inbox | `http://localhost:8025` | Empty inbox |
| Trigger reminder task manually | see below | Email appears in MailHog |

**Manually trigger an interview reminder (without waiting for Beat):**
```bash
# From backend/ directory — requires Redis + Celery Worker running:
python -m celery -A celery_app call tasks.interview_reminders.send_interview_reminders
```

**Or run the standalone test script (no Redis/Celery required):**
```bash
python -X utf8 c:\Users\pooja\.gemini\antigravity-ide\brain\631b7672-19f1-447d-aa6d-f1aaa69ea2a6\scratch\test_interview_reminders.py
```
Then open http://localhost:8025 and look for emails from `noreply@placement-portal.local`.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CELERY_BROKER_URL` | Same as REDIS_URL | Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/1` | Celery result storage |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server hostname (use `localhost` for MailHog) |
| `MAIL_PORT` | `587` | SMTP port (use `1025` for MailHog) |
| `MAIL_USE_TLS` | `true` | SMTP TLS (use `false` for MailHog) |
| `MAIL_USERNAME` | *(blank)* | SMTP email — leave blank for console mode |
| `MAIL_PASSWORD` | *(blank)* | SMTP password / App Password |
| `GCHAT_WEBHOOK_URL` | *(blank)* | Google Chat space webhook URL |
| `SMS_PROVIDER` | `console` | SMS mode: `console` or `twilio` |
| `TWILIO_ACCOUNT_SID` | *(blank)* | Twilio credentials |
| `TWILIO_AUTH_TOKEN` | *(blank)* | Twilio credentials |
| `TWILIO_FROM_NUMBER` | *(blank)* | Twilio sender phone number |

---

## Starting the Workers

You need **three separate terminals** running:

### Terminal 1 — Flask API server (already running)
```bash
cd backend
python app.py
```

### Terminal 2 — Celery worker (processes background jobs)
```bash
cd backend
python run_worker.py
```

### Terminal 3 — Celery Beat scheduler (triggers periodic jobs)
```bash
cd backend
python run_beat.py
```

> **Note:** On Windows, Celery uses the `solo` pool automatically
> (the run_worker.py script detects this and sets it for you).

---

## Background Tasks Reference

### 1. Drive Deadline Reminders (`tasks/drive_reminders.py`)

| Property | Value |
|---|---|
| Task name | `tasks.drive_reminders.send_drive_deadline_reminders` |
| Schedule | Daily at **09:00 UTC** (Celery Beat) |
| Retries | Up to 3 times, 5-minute delay |

**What it does:**
- Queries all open placement drives with a deadline today or tomorrow.
- Finds eligible active students who have **not** applied.
- Sends **Email** reminder to these students.
- Logs to `ReminderHistory` database table to prevent duplicate emails.

**Trigger manually:**
```bash
celery -A celery_app call tasks.drive_reminders.send_drive_deadline_reminders
```

---

### 2. Interview Reminders (`tasks/interview_reminders.py`)

| Property | Value |
|---|---|
| Task name | `tasks.interview_reminders.send_interview_reminders` |
| Schedule | Daily at **08:00 UTC** (Celery Beat) |
| Retries | Up to 3 times, 5-minute delay |

**What it does:**
- Queries all interviews scheduled for today or tomorrow
- Sends **Email** reminder to the student
- Sends **Google Chat** notification (if webhook is configured)
- Sends **SMS** reminder (via the configured provider)

**Trigger manually:**
```bash
celery -A celery_app call tasks.interview_reminders.send_interview_reminders
```

---

### 3. Monthly Placement Report (`tasks/monthly_reports.py`)

| Property | Value |
|---|---|
| Task name | `tasks.monthly_reports.generate_monthly_report` |
| Schedule | 1st of every month at **06:00 UTC** (Celery Beat) |
| Retries | Up to 2 times, 10-minute delay |
| Output | `backend/reports/YYYY-MM/placement_report.html` + `.pdf` |

**What it does:**
- Gathers placement statistics from the database
- Generates an HTML report with metrics, pipeline, company stats, department breakdown
- Generates a PDF report using ReportLab
- Sends a Google Chat summary message

**Trigger via API:**
```
POST /api/admin/reports/generate
Body: { "month": "2026-06" }   ← optional, defaults to previous month
```

**Trigger manually (CLI):**
```bash
celery -A celery_app call tasks.monthly_reports.generate_monthly_report
```

---

### 3. CSV Exports (`tasks/csv_exports.py`)

| Property | Value |
|---|---|
| Task names | `tasks.csv_exports.export_students_csv` / `export_companies_csv` |
| Trigger | On-demand via API (no schedule) |
| Retries | Up to 3 times, 2-minute delay |
| Output | `backend/exports/<type>_export_YYYYMMDD_HHMMSS.csv` |

**Student export columns:**
ID, Name, Email, Register Number, Department, Year, CGPA, Skills, Phone,
Graduation Year, Marks 10th, Marks 12th, Backlogs, Preferred Role,
Placement Status, Account Status, Total Applications, Shortlisted, Interview, Selected, Rejected

**Company export columns:**
ID, Company Name, Industry, Website, City, Contact Person, Contact Email,
Contact Phone, Approval Status, Blacklisted, Account Status,
Total Drives, Total Applications Received, Total Shortlisted, Total Selected

---

## Export API Workflow

```
1. POST /api/admin/export/students
   → Response: { task_id: "abc123", status_url: "/api/admin/export/status/abc123" }

2. GET /api/admin/export/status/abc123
   → Response: { state: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" }
   
3. (When state == "SUCCESS"):
   → Response includes: { download_url: "/api/admin/export/download/students_export_20260726.csv" }

4. GET /api/admin/export/download/students_export_20260726.csv
   → Downloads the CSV file
```

---

## Redis Caching Reference

### Cached Endpoints

| Endpoint | Cache Key Pattern | TTL |
|---|---|---|
| `GET /api/admin/stats` | `admin:stats` | 5 min |
| `GET /api/admin/activities` | `admin:activities` | 2 min |
| `GET /api/admin/reports/stats` | `admin:report_stats` | 10 min |
| `GET /api/admin/students` | `admin:students:{search}:{status}:{page}` | 3 min |
| `GET /api/admin/students/{id}` | `admin:student:{id}` | 3 min |
| `GET /api/admin/companies` | `admin:companies:{search}:{status}:{page}` | 3 min |
| `GET /api/admin/companies/{id}` | `admin:company:{id}` | 3 min |
| `GET /api/admin/drives` | `admin:drives:{status}:{page}` | 3 min |
| `GET /api/admin/drives/{id}` | `admin:drive:{id}` | 3 min |
| `GET /api/student/stats` | `student:stats:{uid}` | 2 min |
| `GET /api/student/profile` | `student:profile:{uid}` | 5 min |
| `GET /api/student/drives` | `student:drives:{uid}:{search}` | 2 min |
| `GET /api/company/stats` | `company:stats:{uid}` | 2 min |
| `GET /api/company/profile` | `company:profile:{uid}` | 5 min |
| `GET /api/company/drives` | `company:drives:{uid}` | 2 min |

### Cache Invalidation Strategy

All write operations (PUT/POST/DELETE) call `cache.delete()` or
`cache.delete_pattern()` immediately after `db.session.commit()`:

- **Student update** → invalidates `admin:students:*`, `admin:student:{id}`, `admin:stats`
- **Apply for drive** → invalidates `student:stats:{uid}`, `student:drives:{uid}:*`, `admin:stats`, `admin:activities`
- **Publish result** → invalidates `company:stats:{uid}`, `admin:stats`, `admin:report_stats`, `student:stats:{uid}`
- **Approve drive** → invalidates `admin:drives:*`, `admin:drive:{id}`, `admin:stats`, `admin:activities`

### Redis Fallback Behaviour

If Redis is **not running**, the cache layer silently disables itself.
All routes continue to work normally — they just hit the database every time.
No errors are thrown. The health check endpoint (`GET /api/health`) shows
the Redis status.

---

## File Outputs

| Type | Location |
|---|---|
| CSV Exports | `backend/exports/*.csv` |
| HTML Reports | `backend/reports/YYYY-MM/placement_report.html` |
| PDF Reports | `backend/reports/YYYY-MM/placement_report.pdf` |
| Beat schedule DB | `backend/celerybeat-schedule.db` |

---

## Notification Services

### Email
- **Console mode** (default): Email content is printed to the log. No SMTP server required.
- **MailHog mode** (local testing): Set `MAIL_SERVER=localhost`, `MAIL_PORT=1025`, `MAIL_USE_TLS=false`. You can view the emails in the MailHog web UI (usually `http://localhost:8025`).
- **SMTP mode** (production): Set `MAIL_SERVER=smtp.gmail.com` and provide `MAIL_USERNAME` / `MAIL_PASSWORD`. Use an App Password for Gmail.

### Google Chat
- Leave `GCHAT_WEBHOOK_URL` blank to skip GChat notifications.
- Sends notifications for: interview reminders, monthly report generation.

### SMS
- **Console mode** (default): SMS content is printed to the log.
- **Twilio mode**: Set `SMS_PROVIDER=twilio` and the three `TWILIO_*` env vars.
- New providers can be added by implementing `SMSProvider` in `services/sms_service.py`.

---

## Monitoring (Optional)

Start the Flower dashboard to see running/completed tasks:
```bash
celery -A celery_app flower --port=5555
# Open: http://localhost:5555
```

---

## Commit Message

```
feat(background): add Celery/Redis async jobs, scheduled reports, CSV exports, interview reminders, and Redis response caching
```
