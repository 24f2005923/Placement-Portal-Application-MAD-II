from flask import request


def json_payload():
    """Return a JSON request body as a dict without repeating Flask boilerplate."""
    return request.get_json(silent=True) or {}


def query_text(name, default=''):
    return request.args.get(name, default).strip()


def pagination_args(default_page=1, default_per_page=20):
    return (
        int(request.args.get('page', default_page)),
        int(request.args.get('per_page', default_per_page)),
    )


def search_status_pagination():
    page, per_page = pagination_args()
    return query_text('search'), query_text('status'), page, per_page


def query_cache_key(prefix, *names):
    values = [request.args.get(name, '').strip().lower() for name in names]
    page = request.args.get('page', 1)
    return ':'.join([prefix, *values, str(page)])
