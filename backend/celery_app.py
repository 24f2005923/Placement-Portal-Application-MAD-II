"""
celery_app.py — Celery application factory
──────────────────────────────────────────
Creates and configures the Celery application so it shares the
same Flask application context.  This lets Celery tasks use
SQLAlchemy models, Flask config, and other Flask extensions exactly
like a normal request would.

Beat Schedule (periodic tasks):
  • send_interview_reminders  — every day at 08:00
  • generate_monthly_report   — 1st of every month at 06:00

How to start workers (run from the backend/ directory):
  # Start the task worker:
  python run_worker.py

  # Start the Beat scheduler (separate terminal):
  python run_beat.py

  # Or use the helper scripts directly with Celery CLI:
  celery -A celery_app worker --loglevel=info
  celery -A celery_app beat   --loglevel=info
"""

from celery import Celery, Task
from celery.schedules import crontab


def create_celery_app(flask_app):
    """
    Bind a Celery instance to the given Flask app.

    The Celery instance uses the broker/backend URLs from the Flask
    config.  A custom Task base class pushes the Flask app context
    before every task runs, so db.session, current_app, etc. all
    work normally inside tasks.

    Args:
        flask_app: The Flask application object (from create_app()).

    Returns:
        A configured Celery application instance.
    """

    class ContextTask(Task):
        """
        Custom base task that wraps execution inside a Flask
        application context.  This is the recommended pattern for
        integrating Celery with Flask.
        """
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config['CELERY_BROKER_URL'],
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        task_cls=ContextTask,
    )

    # ── Celery configuration ──────────────────────────────────────
    celery.conf.update(
        # How long task results are stored in Redis.
        result_expires=flask_app.config['CELERY_RESULT_EXPIRES'],

        # Serialise task arguments and results as JSON (readable, secure).
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],

        # Use UTC for all scheduled times.
        timezone='UTC',
        enable_utc=True,

        # Retry tasks up to 3 times by default before marking as FAILURE.
        task_acks_late=True,
        task_reject_on_worker_lost=True,

        # ── Beat Schedule — periodic tasks ────────────────────────
        beat_schedule={

            # Daily interview reminder — fires every day at 08:00 UTC.
            # Notifies students who have interviews in the next 24–48 hours.
            'daily-interview-reminders': {
                'task': 'tasks.interview_reminders.send_interview_reminders',
                'schedule': crontab(hour=8, minute=0),
            },

            # Monthly placement report — fires on the 1st of every month
            # at 06:00 UTC.  Generates an HTML + PDF placement summary.
            'monthly-placement-report': {
                'task': 'tasks.monthly_reports.generate_monthly_report',
                'schedule': crontab(hour=6, minute=0, day_of_month=1),
            },
        },

        # Discover tasks from these modules automatically.
        imports=[
            'tasks.interview_reminders',
            'tasks.monthly_reports',
            'tasks.csv_exports',
        ],
    )

    return celery


# ── Module-level Celery instance ─────────────────────────────────
# This is what the Celery CLI (and run_worker.py) imports.
# The Flask app is created here so the worker process has a full
# app context available from the start.

def _build_celery():
    """Create Flask app and bind Celery — used by worker/beat processes."""
    from app import create_app
    flask_app = create_app()
    return create_celery_app(flask_app)


# Workers import `celery` from this module.
celery = _build_celery()
