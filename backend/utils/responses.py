from flask import jsonify

def success_response(data=None, message=None, status_code=200):
    """Generates a standardized JSON success response."""
    response = {}
    if message:
        response['message'] = message
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response['data'] = data
    return jsonify(response), status_code

def error_response(error_message, status_code=400):
    """Generates a standardized JSON error response."""
    return jsonify({'error': error_message}), status_code

def created_response(data=None, message="Resource created successfully"):
    """Generates a standardized JSON 201 response."""
    return success_response(data=data, message=message, status_code=201)
