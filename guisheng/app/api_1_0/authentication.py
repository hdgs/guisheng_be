from flask import g, jsonify
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api

auth = HTTPBasicAuth()

@api.route('/token/<int:id>')
def get_token(id):
    user = User.query.get_or_404(id)
    token = user.generate_auth_token(expiration=3600)
    return jsonify({
        'token':token,
        'expiration':3600,
        })
