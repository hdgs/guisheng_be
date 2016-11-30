# coding: utf-8

from . import auth
from flask import request,jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User

@api.route('/register',methods=['GET','POST'])
def register():
    username = request.get_json().get("username")
    email = request.get_json().get("email")
    password = request.get_json().get("password")
    user = User(name=username,
                email=email,
                password=password)
    db.session.add(user)
    db.session.commit()
    user_id=User.query.filter_by(email=email).first().id
    return jsonify({
        "created":user_id,
        })


@api.route('/login', methods=['GET', 'POST'])
def login():
    email = request.get_json().get("email")
    password = request.get_json().get("password")
    try:
        user = User.query.filter_by(username=username).first()
    except:
        user = None
        if user is not None and user.verify_password(password):
            login_user(user)
            uid = user.id
        return jsonify({
            "uid":uid,
            })
