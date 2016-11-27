# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api


@api.route('/pics/<int:id>/', methods=['GET','POST'])
def get_pic(id):
    pic = Picture.query.get_or_404(id)
    return Response(json.dumps({
        "title":pic.title,
        "author":User.query.get_or_404(pic.author_id).name,
        "time":pic.time.strftime('%m/%d/%Y'),
        "pics":pic.img_url,
        "introduction":pic.introduction,
    }),mimetype='application/json')

@api.route('/photos/', methods=['GET','POST'])
def command_pics():
    pic_id = request.get_json().get('article_id')
    pic_tag = Picture.query.get_or_404(pic_id).tag[0]
    all_pics = Picture.query.order_by(Picture.views.desc()).all()
    command_pics = []
    for p in all_pics:
        if p.tag[0]==pic_tag:
            command_pics.append(p)
    return Response(json.dumps([{
            "img_url":pic.img_url,
            "title":pic.title,
            "author":User.query.get_or_404(pic.author_id).name,
            "views":pic.views,
            "tag":pic.tag,
        } for pic in command_pics]
    ),mimetype='application/json')

