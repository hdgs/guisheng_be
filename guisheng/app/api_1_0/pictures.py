# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api


@api.route('/pics/<int:id>/', methods=['GET'])
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
    pic_id = int(request.get_json().get('article_id'))
    now_pic = Picture.query.get_or_404(p_id)
    tag_id = now_pic.tag[0].tag_id
    tag = Tag.query.get_or_404(tag_id)
    pics = []
    for _pic in tag.pictures:
        pics.append(_pic.picture_id)
    sortlist = sorted(news,key=lambda id: News.query.get_or_404(id).views,reverse=True) 
    command_pics = sortlist[:3]
    return Response(json.dumps([{
            "img_url":pic.img_url,
            "title":pic.title,
            "author":User.query.get_or_404(pic.author_id).name,
            "views":pic.views,
            "tag":pic_tag,
        } for pic in command_pics]
    ),mimetype='application/json')

