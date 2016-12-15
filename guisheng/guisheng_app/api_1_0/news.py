# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,PostTag,Tag
from . import api
from .. import db
from guisheng_app.decorators import admin_required

@api.route('/news/<int:id>/', methods=['GET'])
def get_news(id):
    news = News.query.get_or_404(id)
    news.views+=1
    db.session.commit()
    return Response(json.dumps({
        "title":news.title,
        "author":User.query.get_or_404(news.author_id).name,
        "time":news.time.strftime('%m/%d/%Y'),
        "body":news.body,
        }),mimetype='application/json')


@api.route('/recommend_news/recommend/', methods=['GET','POST'])
def recommend_news():
    news_id = int(request.get_json().get('article_id'))
    now_news = News.query.get_or_404(news_id)
    try:
        tag_id = now_news.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        news = []
        for _news in tag.news:
            news.append(_news.news_id)
        sortlist = sorted(news,key=lambda id: News.query.get_or_404(id).views,reverse=True)
        recommend_news = sortlist[:3] if len(sortlist)>=4 else sortlist
    except:
        recommend_news=[]
    return Response(json.dumps([{
            "title":News.query.filter_by(id=news_id).first().title,
            "description":News.query.filter_by(id=news_id).first().description,
            "author":User.query.get_or_404(News.query.filter_by(id=news_id).first().author_id).name,
            "tag":tag.body,
            "views":News.query.filter_by(id=news_id).first().views
        }for news_id in recommend_news]
    ),mimetype='application/json')

@api.route('/news/', methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "POST":
        news = News.from_json(request.get_json())
        db.session.add(news)
        db.session.commit()
        return jsonify({
            'id': news.id
        }), 201

@api.route('/news/<int:id>/', methods=["GET", "PUT"])
@admin_required
def update_news(id):
    news = News.query.get_or_404(id)
    json = request.get_json()
    if request.method == "PUT":
        news.title = json.get('title')
        news.img_url = json.get('img_url')
        news.author = json.get('author')
        news.description = json.get('description')
        news.author =  User.query.get_or_404(json.get('author_id'))
        db.session.add(news)
        db.session.commit()
        return jsonify({
            'update': news.id
        }), 200

@api.route('/news/<int:id>/body/', methods=["GET", "PUT"])
@admin_required
def update_news_body(id):
    news = News.query.get_or_404(id)
    if request.method == "PUT":
        news.body = request.get_json().get('body')
        db.session.add(news)
        db.session.commit()
        return jsonify({
            'update': news.id
        }), 200

@api.route('/news/<int:id>/', methods=["GET", "DELETE"])
@admin_required
def delete_news(id):
    news = News.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(news)
        db.session.commit()
        return jsonify({
            'deleted': news.id
        }), 200
 
