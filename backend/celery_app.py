

try:
    from celery import Celery, Task
    from celery.schedules import crontab
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    class Task:
        def __init__(self):
            self.request = type('TaskRequest', (), {'id': 'mock_task_id'})()
        def retry(self, exc=None):
            raise exc

    class MockAsyncResult:
        def __init__(self, task_id, state='SUCCESS', result=None):
            self.id = task_id
            self.state = state
            self.result = result

    class Celery:
        def __init__(self, *args, **kwargs):
            self.conf = type('Conf', (), {'update': lambda *a, **k: None})()
        def task(self, *args, **kwargs):
            def decorator(fn):
                def wrapper(*w_args, **w_kwargs):
                    if kwargs.get('bind'):
                        return fn(Task(), *w_args, **w_kwargs)
                    return fn(*w_args, **w_kwargs)
                def delay(*d_args, **d_kwargs):
                    try:
                        res = wrapper(*d_args, **d_kwargs)
                    except Exception as e:
                        res = {'status': 'failed', 'error': str(e)}
                    return MockAsyncResult('mock_task_id', 'SUCCESS', res)
                wrapper.delay = delay
                wrapper.retry = lambda exc=None: None
                return wrapper
            return decorator
        def AsyncResult(self, task_id):
            return MockAsyncResult(task_id, 'SUCCESS', {'status': 'completed'})

    def crontab(*args, **kwargs):
        return None


def create_celery_app(flask_app):

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config['CELERY_BROKER_URL'],
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        task_cls=ContextTask,
    )

    celery.conf.update(
        result_expires=flask_app.config['CELERY_RESULT_EXPIRES'],

        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],

        timezone='UTC',
        enable_utc=True,

        task_acks_late=True,
        task_reject_on_worker_lost=True,

        beat_schedule={
            'daily-interview-reminders': {
                'task': 'tasks.interview_reminders.send_interview_reminders',
                'schedule': crontab(hour=8, minute=0),
            },

            'monthly-placement-report': {
                'task': 'tasks.monthly_reports.generate_monthly_report',
                'schedule': crontab(hour=6, minute=0, day_of_month=1),
            },

            'daily-drive-reminders': {
                'task': 'tasks.drive_reminders.send_drive_deadline_reminders',
                'schedule': crontab(hour=9, minute=0),
            },

           
            'weekly-login-reminder': {
                'task': 'tasks.announcements.weekly_login_reminder',
                'schedule': crontab(hour=10, minute=0, day_of_week='monday'),
            },
        },

        imports=[
            'tasks.interview_reminders',
            'tasks.monthly_reports',
            'tasks.csv_exports',
            'tasks.drive_reminders',
            'tasks.announcements',
        ],
    )

    return celery


def _build_celery():
    from app import create_app
    flask_app = create_app()
    return create_celery_app(flask_app)


celery = _build_celery()
