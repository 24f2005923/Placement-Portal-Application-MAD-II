from models import db


def cleaned_text(value, lower=False):
    text = str(value or '').strip()
    return text.lower() if lower else text


def apply_ilike_search(query, search_term, fields):
    """Apply a project-standard wildcard search across SQLAlchemy columns."""
    clean_search = cleaned_text(search_term)
    if not clean_search:
        return query

    wildcard = f"%{clean_search}%"
    return query.filter(db.or_(*(field.ilike(wildcard) for field in fields)))


def paginate_named_items(query, page_num, records_per_page, response_key, mapper=lambda item: item.to_dict()):
    """Paginate a query and expose items under the API's expected response key."""
    from utils.pagination import paginate_query

    paginated = paginate_query(query, page_num, records_per_page)
    paginated[response_key] = [mapper(item) for item in paginated.pop('items')]
    return paginated
