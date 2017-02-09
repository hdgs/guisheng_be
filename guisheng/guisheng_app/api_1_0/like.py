# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Like
from . import api
from .. import db

@api.route('/like/picture/', methods=['GET','POST'])
def like_picture():
    if request.method == 'POST':
        like = Like()
        like.picture_id = int(request.get_json().get('picture_id'))
        db.session.add(like)
        db.session.commit()
        return jsonify({
            'status':200
        })

@api.route('/like/comment/', methods=['GET','POST'])
def like_comment():
    if request.method == 'POST':
        like = Like()
        like.comment_id = int(request.get_json().get('comment_id'))
        db.session.add(like)
        db.session.commit()
        return jsonify({
            'status':200
        })
