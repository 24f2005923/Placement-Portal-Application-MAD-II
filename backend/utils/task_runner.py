import logging
import socket
from urllib.parse import urlparse
from flask import jsonify

logger = logging.getLogger(__name__)


def dispatch_task(task, **kwargs):
    """
    Queue a Celery task when the broker is available; otherwise execute the
    same task synchronously for local development.
    """
    if not _broker_is_reachable(task):
        logger.warning('Celery broker unavailable; running %s synchronously.', getattr(task, 'name', repr(task)))
        return _run_task_locally(task, kwargs)

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
        return _run_task_locally(task, kwargs)


def task_dispatch_response(dispatched, queued_message, completed_message, status_url_prefix, download_url_builder=None):
    """Build the public JSON response for a task that was queued or run locally."""
    result = dispatched['result'] or {}
    download_url = download_url_builder(result) if download_url_builder else result.get('download_url')
    status_code = 202 if dispatched['queued'] else 200

    return jsonify({
        'message': queued_message if dispatched['queued'] else completed_message,
        'task_id': dispatched['task_id'],
        'status_url': f"{status_url_prefix}/{dispatched['task_id']}",
        'state': 'PENDING' if dispatched['queued'] else 'SUCCESS',
        'result': result,
        'download_url': download_url,
    }), status_code


def async_result_response(task_id, async_result, download_url_builder=None, pending_message='Task is waiting in the queue.'):
    """Build a consistent task-status response from a Celery AsyncResult."""
    state = async_result.state
    response = {
        'task_id': task_id,
        'state': state,
    }

    if state == 'SUCCESS':
        result = async_result.result or {}
        response['result'] = result
        download_url = download_url_builder(result) if download_url_builder else result.get('download_url')
        if download_url:
            response['download_url'] = download_url
    elif state == 'FAILURE':
        response['error'] = str(async_result.result)
    elif state == 'PENDING':
        response['message'] = pending_message
    elif state == 'STARTED':
        response['message'] = 'Task is currently running.'

    return jsonify(response), 500 if state == 'FAILURE' else 200


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


def _run_task_locally(task, kwargs):
    result = task.run(**kwargs)
    return {
        'queued': False,
        'task_id': 'local-sync',
        'result': result,
    }


def _broker_is_reachable(task):
    broker_url = getattr(getattr(task, 'app', None), 'conf', {}).get('broker_url')
    if not broker_url:
        return True

    parsed = urlparse(str(broker_url))
    if parsed.scheme not in ('redis', 'rediss', 'amqp', 'pyamqp'):
        return True

    host = parsed.hostname or 'localhost'
    port = parsed.port or (6379 if parsed.scheme in ('redis', 'rediss') else 5672)
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False
