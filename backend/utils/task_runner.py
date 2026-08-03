import logging

logger = logging.getLogger(__name__)


def dispatch_task(task, **kwargs):
    """
    Queue a Celery task when the broker is available; otherwise execute the
    same task synchronously for local development.
    """
    try:
        queued = task.delay(**kwargs)
        return {
            'queued': True,
            'task_id': queued.id,
            'result': None,
        }
    except Exception as exc:
        if not _looks_like_broker_error(exc):
            raise

        logger.warning(
            'Celery broker unavailable; running %s synchronously: %s',
            getattr(task, 'name', repr(task)),
            exc,
        )
        eager_result = task.apply(kwargs=kwargs)
        if eager_result.failed():
            raise eager_result.result

        return {
            'queued': False,
            'task_id': eager_result.id or 'local-sync',
            'result': eager_result.result,
        }


def _looks_like_broker_error(exc):
    text = str(exc).lower()
    module_name = exc.__class__.__module__.lower()
    class_name = exc.__class__.__name__.lower()
    return (
        'kombu' in module_name
        or 'redis' in module_name
        or 'operationalerror' in class_name
        or 'connection refused' in text
        or 'error 10061' in text
        or 'no connection could be made' in text
    )
