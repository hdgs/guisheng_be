# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api


@api.route('/profile/<int:id>/', methods=['GET','POST','PUT'])
def profile(id):
    if request.method == 'GET':
        user = User.query.get_or_404(id)
        return Response(json.dumps({
            "img_url":user.img_url,
            "name":user.name,
            "weibo":user.weibo,
            "introduction":user.introduction,
            "works":','.join([inews.title for inews in user.news.all()])+
                    ','.join([pic.title for pic in user.pictures.all()])+
                    ','.join([article.title for article in user.articles.all()])+
                    ','.join([interaction.title for interaction in user.interactions.all()]),
            #"collection":user.collection,
            "suggestion":user.suggestion,
            }),mimetype='application/json')

    if request.method == 'PUT':
        user = User.query.get_or_404(id)
        user.img_url = request.get_json().get("img_url")
        user.name = request.get_json().get("name")
        user.weibo = request.get_json().get("weibo")
        user.ntroduction = request.get_json().get("introduction")
        user.suggestion = request.get_json().get("suggestion")
        db.session.add(user)
        db.session.commit()
        return Response(json.dumps({
            "img_url":user.img_url,
            "name":user.name,
            "weibo":user.weibo,
            "introduction":user.introduction,
            "works":','.join([inews.title for inews in user.news.all()])+
                    ','.join([pic.title for pic in user.pictures.all()])+
                    ','.join([article.title for article in user.articles.all()])+
                    ','.join([interaction.title for interaction in user.interactions.all()]),
            #"collection":user.collection,
            "suggestion":user.suggestion,
            }),mimetype='application/json')


