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
        "time":pic.time.strftime('%Y-%m-%d %H:%M:%S %f'),
        "pics":pic.img_url,
        "introduction":pic.introduction,
    }),mimetype='application/json')

@api.route('/photos/', methods=['GET','POST'])
def get_photos():
    photos = Picture.query.order_by(Picture.views.desc()).limit(10)
    return Response(json.dumps([{
            "img_url":photo.img_url,
            "title":photo.title,
            "author":User.query.get_or_404(photo.author_id).name,
            "views":photo.views,
            "tag":photo.tag,
        } for photo in photos]
    ),mimetype='application/json')


