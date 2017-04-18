from functools import wraps
from flask import abort, request, g, jsonify
from flask_login import current_user
from guisheng_app.models import User
import base64

def admin_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token_header = request.headers.get('Authorization',None)
        if token_header:
            token_hash = token_header[6:]
            decode_token = base64.b64decode(token_hash)
            token = decode_token
            g.current_user = User.verify_auth_token(token)
            if not g.current_user.is_administrator():
                return jsonify({'message': '403 Forbidden'}), 403
            return f(*args,**kwargs)
        else:
            return jsonify({'message': '401 unAuthorization'}), 401
    return decorated


