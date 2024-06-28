from flask import request

def paginate(query, filter, page, per_page):
    total = query.collection.count_documents(filter) 
    if per_page > total:
        per_page = total  
    items = query.skip((page - 1) * per_page).limit(per_page)
    return {
        'total': total,
        'page': page,
        'per_page': per_page,
        'items': list(items)
    }

def get_pagination_params():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    return page, per_page
