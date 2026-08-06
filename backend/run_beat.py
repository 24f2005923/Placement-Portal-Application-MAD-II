"""
run_beat.py — Celery Beat scheduler launcher
──────────────────────────────────────────────
Run this script in a SEPARATE terminal to start the periodic task
scheduler.  Beat wakes up on a schedule and sends tasks to the
worker queue.

Usage (from the backend/ directory — open a new terminal):
  python run_beat.py

This is equivalent to:
  celery -A celery_app beat --loglevel=info

Scheduled tasks (defined in celery_app.py):
  • send_interview_reminders  — daily at 08:00 UTC
  • generate_monthly_report   — 1st of every month at 06:00 UTC

Notes:
  • Beat does NOT execute tasks — it only schedules them.
    You also need the worker running (run_worker.py).
  • Only one Beat instance should run at a time.
  • The schedule state is stored in celerybeat-schedule.db in the
    current directory.
"""

import sys
import os

# Add the backend directory to sys.path so all imports resolve correctly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery_app import celery


if __name__ == '__main__':
    print('Starting Celery Beat scheduler ...')
    print('Scheduled tasks:')
    print('  - Interview reminders: daily at 08:00 UTC')
    print('  - Monthly placement report: 1st of every month at 06:00 UTC')
    print('Press Ctrl+C to stop.\n')

    celery.start(argv=[
        'beat',
        '--loglevel=info',
        '--scheduler=celery.beat:PersistentScheduler',
    ])
