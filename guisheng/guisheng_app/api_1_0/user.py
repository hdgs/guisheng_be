# coding: utf-8

from . import api
from guisheng_app import db
from flask import request,jsonify,Response
from flask_login import login_user, logout_user, current_user, login_required
from guisheng_app.models import User
from guisheng_app.decorators import admin_required

@api.route('/register/',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.get_json().get("username")
        email = request.get_json().get("email")
        password = request.get_json().get("password")
        if not User.query.filter_by(name=name).first():
            user = User(name=name,
                    email=email,
                    password=password)
            db.session.add(user)
            db.session.commit()
            user_id=User.query.filter_by(email=email).first().id
            return jsonify({
                "created":user_id,
            })

@api.route('/login/', methods=['GET', 'POST'])
def login():
    email = request.get_json().get("email")
    password = request.get_json().get("password")
    try:
        user = User.query.filter_by(email=email).first()
    except:
        user = None
        uid = None
    if user is not None and user.verify_password(password):
        login_user(user)
        uid = user.id
        token = user.generate_auth_token()
        return jsonify({
            "uid":user.id,
            "token":token,
        })

#-----------------------------------后台管理API---------------------------------------
@api.route('/role/author/<int:id>/', methods=['GET'])
@admin_required
def change_to_author(id):
    user = User.query.get_or_404(id)
    user.user_role = 1
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "update":user.id,
        }),200

@api.route('/role/user/<int:id>/', methods=['GET'])
@admin_required
def change_to_common_user(id):
    user = User.query.get_or_404(id)
    user.user_role = 0
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "update":user.id,
        }),200
