

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
