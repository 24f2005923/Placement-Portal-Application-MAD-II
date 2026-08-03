# Placement Portal Application

A role-based placement management application for admins, companies, and
students. The system manages student registration, company registration,
placement drives, applications, interviews, results, reports, exports, and
email notifications.

## Fresh Clone Behavior

No dummy data is committed or loaded automatically.

On first backend startup:

- `backend/database/placement.db` is generated automatically.
- Database tables are created automatically.
- Runtime folders for uploads, exports, and reports are created automatically.
- Only the optional bootstrap admin account is created when `SEED_ADMIN=true`.

Configure first-run behavior in `backend/.env`.

## Run Locally

Backend:

```bash
cd backend
copy .env.example .env
pip install -r requirements.txt
python app.py
```

Frontend:

```bash
npm install
npm run dev
```

MailHog email setup:

```text
See MAILHOG_SETUP.md
```

## Local URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5000 |
| MailHog inbox | http://localhost:8025 |

## Default Admin

When `SEED_ADMIN=true` in `backend/.env`:

```text
Email: admin@admin.com
Password: password
```

Change these values in `.env` before running on a shared machine.
