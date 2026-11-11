# Placement Portal Application (MAD-II)

A full-stack university placement portal for managing student registrations, company profiles, placement drives, applications, interviews, and reports. The project includes a Flask REST API backend, a Vue 3 frontend, SQLite persistence, and background task processing via Celery and Redis.

## Overview

This system supports three core user roles:

- Students: register, update profile, apply for drives, upload resume, track application progress.
- Companies: register, manage placement drives, shortlist candidates, schedule interviews, publish results.
- Admins: manage users, review company requests, monitor applications, generate reports, and export data.

## Tech Stack

### Frontend
- Vue 3
- Vite
- Bootstrap 5
- Vue Router
- Axios

### Backend
- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- SQLite
- Celery + Redis
- ReportLab
- Flask-CORS

## Project Structure

```text
Placement-Portal-Application-MAD-II/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── MailHog.exe
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── tasks/
│   ├── utils/
│   ├── cache/
│   ├── middleware/
│   ├── reports/
│   ├── exports/
│   └── uploads/
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── src/
│   └── node_modules/
├── api.yaml
├── check_cascade.py
└── README.md
```

## Key Features

- Student authentication and profile management
- Company registration with admin approval flow
- Placement drive creation and publishing
- Student application submission and status tracking
- Interview scheduling and result publication
- Resume upload and export support
- Admin dashboard statistics and activity views
- CSV export and report generation
- Background reminders and notifications using Celery/Redis
- Email notifications via MailHog in local development

## API Documentation

The project includes an OpenAPI specification in [api.yaml](api.yaml). It describes the backend endpoints for authentication, admin operations, company operations, and student functionality.

## Prerequisites

Before running the project, make sure the following are installed:

- Python 3.10+
- Node.js 18+
- npm
- Redis (required for Celery and caching)
- Optional: MailHog for local email testing

## Backend Setup

1. Open a terminal in the project root.
2. Go to the backend folder:

```bash
cd backend
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

- Windows:

```bash
venv\Scripts\activate
```

- macOS/Linux:

```bash
source venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Copy the example environment file and update values if needed:

```bash
copy .env.example .env
```

7. Start Redis.

For Windows, Redis can be installed through Memurai or a local Redis service. For local dev, the app defaults to:

```text
redis://localhost:6379/0
```

8. Start MailHog if you want to capture emails locally:

```bash
cd backend
MailHog.exe
```

Then open:

```text
http://localhost:8025
```

9. Run the Flask app:

```bash
python app.py
```

The backend will run on:

```text
http://localhost:5000
```

## Frontend Setup

1. Open a new terminal in the project root.
2. Go to the frontend folder:

```bash
cd frontend
```

3. Install dependencies:

```bash
npm install
```

4. Start the Vue dev server:

```bash
npm run dev
```

The frontend will run on:

```text
http://localhost:5173
```

## Background Workers

This project uses Celery for asynchronous tasks such as reminders and reporting.

Start the worker:

```bash
cd backend
python -m celery -A celery_app worker --loglevel=info
```

Start the beat scheduler:

```bash
cd backend
python -m celery -A celery_app beat --loglevel=info
```

## Default Admin Login

The app seeds a default admin account if enabled in the environment configuration.

```text
Email: admin@admin.com
Password: password
```

You can adjust these values in the backend `.env` file.

## Notes

- The backend automatically creates the SQLite database and required tables when it starts.
- The app stores uploaded resumes in `backend/uploads/resumes/`.
- Exported files and generated reports are saved under `backend/exports/` and `backend/reports/`.
- The app uses CORS to allow local frontend access from `http://localhost:5173`.

## License

This project is intended for academic and portfolio use. Please check repository ownership and licensing before production deployment or redistribution.

## Contributing

Contributions are welcome. For feature improvements or bug fixes, create a branch, make the changes, and submit a pull request with a clear summary.
