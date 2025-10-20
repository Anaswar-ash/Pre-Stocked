from functools import wraps

from flask import request

from .errors import bad_request


def validate_ticker(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ticker = request.form.get("ticker").upper()
        if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
            return bad_request("Invalid ticker symbol.")
        return f(*args, **kwargs)
    return decorated_function
