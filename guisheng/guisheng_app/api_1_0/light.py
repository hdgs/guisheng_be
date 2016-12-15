# coding: utf-8
import ast
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api

@api.route('/light/',methods=['GET','POST'])
def light():
    light = Light()
    light.like_degree = int(request.get_json().get("like_degree"))
    kind = int(request.get_json().get("kind"))

    post_kind = {1: News, 2: Picture, 3: Article, 4: Interaction}.get(kind)
    _ids = {1: "news_id", 2: "picture_id", 3: "article_id", 4: "interaction_id" }.get(kind)
    c_id = ast.literal_eval(_ids)
    light.c_id = request.get_json().get("article_id")
    
    db.session.add(light)
    db.session.commit()
    return jsonify({
        "status":200
    })

