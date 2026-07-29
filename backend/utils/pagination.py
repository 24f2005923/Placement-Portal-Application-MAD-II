def paginate_query(query, page_num, records_per_page=20):
    """
    Paginates a SQLAlchemy query.
    Returns a dictionary containing the list of items and pagination metadata.
    """
    if page_num < 1:
        page_num = 1
        
    total_records = query.count()
    offset_val = (page_num - 1) * records_per_page
    items_list = query.offset(offset_val).limit(records_per_page).all()
    
    total_pages = (total_records + records_per_page - 1) // records_per_page if total_records > 0 else 0
    
    return {
        'items': items_list,
        'total': total_records,
        'page': page_num,
        'pages': total_pages
    }
