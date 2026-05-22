# smart_school_backend/utils/request_id.py
"""
Request ID Middleware for tracking requests across logs.

Adds a unique request ID to each HTTP request that can be used
to trace requests across all logs.
"""

import logging
import uuid
from flask import request, g
from functools import wraps

logger = logging.getLogger(__name__)

def generate_request_id():
    """Generate a unique request ID"""
    return str(uuid.uuid4())[:8]

def get_request_id():
    """Get the current request ID from the request context"""
    return getattr(g, 'request_id', None)

class RequestIDMiddleware:
    """WSGI middleware to add request ID to each request"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Generate request ID
        request_id = generate_request_id()
        
        # Store in environ for access
        environ['HTTP_X_REQUEST_ID'] = request_id
        
        def custom_start_response(status, headers, exc_info=None):
            # Add request ID to response headers
            headers.append(('X-Request-ID', request_id))
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

def init_request_id(app):
    """Initialize request ID for Flask app"""
    @app.before_request
    def before_request():
        g.request_id = generate_request_id()
    
    @app.after_request
    def after_request(response):
        # Add request ID to response headers
        request_id = getattr(g, 'request_id', None)
        if request_id:
            response.headers['X-Request-ID'] = request_id
        return response
    
    # Add logging filter to include request ID
    class RequestIDFilter(logging.Filter):
        def filter(self, record):
            record.request_id = getattr(g, 'request_id', 'no-request-id')
            return True
    
    # Add filter to all loggers
    for logger_name in ['werkzeug', 'flask', 'app']:
        log = logging.getLogger(logger_name)
        log.addFilter(RequestIDFilter())
    
    return app
