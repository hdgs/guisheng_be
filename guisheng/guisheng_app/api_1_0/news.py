# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,News,PostTag,Tag
from . import api
from .. import db
from guisheng_app.decorators import admin_required

@api.route('/news/<int:id>/', methods=['GET'])
def get_news(id):
    news = News.query.get_or_404(id)
    like_degree_one = news.light.filter_by(like_degree=0).count()
    like_degree_two = news.light.filter_by(like_degree=1).count()
    like_degree_three = news.light.filter_by(like_degree=2).count()
    news.views+=1
    db.session.commit()
    return Response(json.dumps({
        "kind":1,
        "title":news.title,
        "author":User.query.get_or_404(news.author_id).name,
        "time":news.time.strftime('%Y-%m-%d'),
        "body":news.body,
        "like_degree":[like_degree_one,like_degree_two,like_degree_three],
        "editor":news.editor,
        "author_id":news.author_id,
    	"commentCount":news.comments.count(),
        "music":{
                "title":"",
                "music_img_url":"",
                "music_url":"",
                "singer":""
        },
        "film":{
               "film_url":"",
               "scores":"",
               "film_img_url":""
        }
        }),mimetype='application/json')


@api.route('/news/recommend/', methods=['GET','POST'])
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
            "title":News.query.get_or_404(news_id).title,
            "description":News.query.get_or_404(news_id).description,
            "author":User.query.get_or_404(News.query.get_or_404(news_id).author_id).name,
            "tag":tag.body,
            "views":News.query.get_or_404(news_id).views,
            "kind":News.query.get_or_404(news_id).kind,
            "article_id":News.query.get_or_404(news_id).id
        }for news_id in recommend_news]
    ),mimetype='application/json')

#----------------------------后台管理API---------------------------------
@api.route('/news/', methods=["GET", "POST"])
#@admin_required
def add_news():
    if request.method == "POST":
        news = News.from_json(request.get_json())
        db.session.add(news)
        db.session.commit()
        tags = request.get_json().get('tags')
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            news_tags = [t.tag_id for t in news.tag.all()]
            if get_tag.id not in news_tags:
                post_tag = PostTag(news_tags=get_tag,news=news)
                db.session.add(post_tag)
                db.session.commit()
        return jsonify({
            'id': news.id
        }), 201

@api.route('/news/<int:id>/', methods=["GET", "PUT"])
#@admin_required
def update_news(id):
    news = News.query.get_or_404(id)
    if request.method == "PUT":
        news.title = request.get_json().get('title')
        news.description = request.get_json().get('description')
        news.author = User.query.filter_by(name=request.get_json().get('name')).first()
        db.session.add(news)
        db.session.commit()

        tags = request.get_json().get('tags')
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            news_tags = [t.tag_id for t in news.tag.all()]
            if get_tag.id not in news_tags:
                post_tag = PostTag(news_tags=get_tag,news=news)
                db.session.add(post_tag)
                db.session.commit()

        tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
        news_tag_ids = [t.tag_id for t in news.tag.all()]
        for news_tag_id in news_tag_ids:
            if  news_tag_id not in tags_id:
                n_tag = Tag.query.get_or_404(news_tag_id)
                post_tag = PostTag.query.filter_by(news_tags=n_tag,news=news).first()
                db.session.delete(post_tag)
                db.session.commit()

        return jsonify({
            'update': news.id
        }), 200

@api.route('/news/<int:id>/body/', methods=["GET", "PUT"])
#@admin_required
def update_news_body(id):
    news = News.query.get_or_404(id)
    if request.method == "PUT":
        news.body = request.get_json().get('body')
        db.session.add(news)
        db.session.commit()
        return jsonify({
            'update': news.id
        }), 200

@api.route('/news/<int:id>/', methods=["DELETE"])
#@admin_required
def delete_news(id):
    news = News.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(news)
        db.session.commit()
        return jsonify({
            'deleted': news.id
        }), 200
 
