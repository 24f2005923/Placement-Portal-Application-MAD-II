"""
run_worker.py — Celery worker launcher
───────────────────────────────────────
Run this script to start the Celery task worker that processes
background jobs (CSV exports, report generation, etc.).

Usage (from the backend/ directory):
  python run_worker.py

This is equivalent to:
  celery -A celery_app worker --loglevel=info --concurrency=2

Notes:
  • Redis must be running before starting the worker.
  • For production, use a process manager like supervisord or systemd
    to keep the worker alive after restarts.
  • On Windows, Celery requires the 'solo' pool (no multiprocessing).
    This is set automatically below.
"""

import sys
import os

# Add the backend directory to sys.path so all imports resolve correctly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery_app import celery


if __name__ == '__main__':
    # Detect Windows and use the solo pool (Celery limitation on Windows).
    is_windows = sys.platform.startswith('win')
    pool_type  = 'solo' if is_windows else 'prefork'

    print(f'Starting Celery worker (pool={pool_type}) ...')
    print('Make sure Redis is running on localhost:6379')
    print('Press Ctrl+C to stop.\n')

    celery.worker_main(argv=[
        'worker',
        '--loglevel=info',
        f'--pool={pool_type}',
        '--concurrency=2',           # 2 parallel worker threads
        '--hostname=placement-worker@%h',
    ])
