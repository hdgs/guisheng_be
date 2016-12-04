from functools import wraps
from flask import abort, request, g
from flask_login import current_user
from app.models import User
import base64

def admin_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token_header = request.headers.get('Authorization',None)
        if token_header:
            token_hash = token_header.split()[1]
            token = base64.b64decode(token_hash)[:-1]
            g.current_user = User.verify_auth_token(token)
            if not g.current_user.is_administrator():
                abort(403)
            return f(*args,**kwargs)
        else:
            abort(401)
    return decorated


