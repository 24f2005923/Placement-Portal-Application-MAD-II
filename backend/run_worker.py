

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
