import os
from functools import wraps
from flask import request, jsonify
import uuid

def clerk_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request.user_id = "00000000-0000-0000-0000-000000000001"
        return f(*args, **kwargs)
    return decorated