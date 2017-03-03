# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Light
from . import api
from guisheng_app import db

@api.route('/light/',methods=['GET','POST'])
def light():
    if request.method == 'POST':
        light = Light()
        light.like_degree = int(request.get_json().get("like_degree"))
        kind = int(request.get_json().get("kind"))
        if kind == 1:
            light.news_id = request.get_json().get("article_id") 
        if kind == 2:
            light.picture_id = request.get_json().get("article_id")
        if kind == 3:
            light.article_id = request.get_json().get("article_id")
        if kind == 4:
            light.interaction_id = request.get_json().get("article_id")
        db.session.add(light)
        db.session.commit()
        return jsonify({
            "status":200
        })

