# coding: utf-8
from flask import render_template,jsonify,Response,g,request,current_app,send_from_directory
from flask_login import current_user
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment,Suggestion,Tag
from . import api
from .. import db
import os
from operator import attrgetter
import time

@api.route('/profile/<int:id>/',methods=['GET'])
def get_profile(id):
    user=User.query.get_or_404(id)
    try:
    	user_role = 1 if current_user.user_role==1 else 0
    except:
        user_role = 0
    return Response(json.dumps({
        "img_url":user.img_url,
        "name":user.name,
        "weibo":user.weibo,
        "introduction":user.introduction,
        "role":user.user_role,
        "user_role":user_role,
        "user_id":user.id
    }),mimetype='application/json')

@api.route('/profile/<int:id>/edit/',methods=['GET','PUT'])
def edit_profile(id):
    if request.method == 'PUT':
        user = User.query.get_or_404(id)
        user.img_url = request.get_json().get("img_url")
        user.name = request.get_json().get("name")
        user.weibo = request.get_json().get("weibo")
        user.introduction = request.get_json().get("introduction")
        db.session.add(user)
        db.session.commit()
        try:
            user_role = 1 if current_user.user_role==1 else 0
        except:
            user_role = 0
        return Response(json.dumps({
            "user_id":user.id,
            "role":user.user_role,
            "user_role":user_role,
            "img_url":user.img_url,
            "name":user.name,
            "weibo":user.weibo,
            "introduction":user.introduction,
            }),mimetype='application/json')

@api.route('/profile/<int:id>/works/',methods=['GET'])
def get_works(id):
    user= User.query.get_or_404(id)
    articles = [article for article in user.articles.all()]
    articles.sort(key=attrgetter('time'),reverse=True)
    return Response(json.dumps([{
            "article_id":_article.id,
            "img_url":_article.img_url[0],
            "title":_article.title,
            "author":user.name,
            "views":_article.views,
            "tag":Tag.query.get_or_404(Article.query.get_or_404(_article.id).tag[0].tag_id).body\
                  if len([i for i in Article.query.get_or_404(_article.id).tag]) else "",
            "description":_article.description,
        }for _article in articles]
    ),mimetype='application/json')


@api.route('/profile/<int:id>/collections/',methods=['GET'])
def get_collections(id):
    user= User.query.get_or_404(id)
    alist = []
    for _collection in Collect.query.filter_by(author_id=id).all():
        if News.query.get_or_404(_collection.news_id):
            news = News.query.get_or_404(_collection.news_id)
            alist.append(news)
        elif Article.query.get_or_404(_collection.article_id):
            article = Article.query.get_or_404(_collection.article_id)
            alist.append(article)
        elif Picture.query.get_or_404(_collection.picture_id):
            picture = Picture.query.get_or_404(_collection.picture_id)
            alist.append(picture)
        elif Interaction.query.get_or_404(_collection.interaction_id):
            interaction = Interaction.query.get_or_404(_collection.interaction_id)
            alist.append(interaction)
    alist.sort(key=attrgetter('time'),reverse=True)
    return Response(json.dumps([{
            "article_id":content.id,
            "img_url":content.img_url[0],
            "title":content.title,
            "author":user.name,
            "views":content.views,
            "tag":Tag.query.get_or_404(content.__class__.query.get_or_404(content.id).tag[0].tag_id).body\
                  if len([i for i in content.__class__.query.get_or_404(content.id).tag]) else "",
            "description":content.description,
        }for content in alist]
    ),mimetype='application/json')


@api.route('/profile/<int:id>/suggestions/',methods=['GET','POST'])
def suggeston(id):
    if request.method == 'POST':
        s = Suggestion()
        s.body = request.get_json().get("body")
        s.contact_information = request.get_json().get("contact_information")
        db.session.add(s)
        db.session.commit()
        return Response(json.dumps({
            'status':200,
            's_id':s.id
            }),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
