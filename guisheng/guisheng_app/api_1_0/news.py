# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,News,PostTag,Tag,Collect
from . import api
from .. import db
from guisheng_app.decorators import admin_required


@api.route('/news/<int:id>/', methods=['POST'])
def get_news(id):
    if request.method == "POST":
        my_id = int(request.get_json().get('my_id'))
        news = News.query.get_or_404(id)
        if news.published == 1:
            like_degree_one = news.light.filter_by(like_degree=0).count()
            like_degree_two = news.light.filter_by(like_degree=1).count()
            like_degree_three = news.light.filter_by(like_degree=2).count()
            news.views+=1
            db.session.commit()
            if my_id == -1:
                collected=0
            else:
                if Collect.query.filter_by(news_id=id).filter_by(author_id=my_id).first():
                    collected=1
                else:
                    collected=0
            return Response(json.dumps({
                "img_url":User.query.get_or_404(news.author_id).img_url,
                "kind":1,
                "title":news.title,
                "author":User.query.get_or_404(news.author_id).name,
                "time":news.time.strftime('%Y-%m-%d'),
                "body":news.body,
                "like_degree":[like_degree_one,like_degree_two,like_degree_three],
                "editor":news.editor,
                "author_id":news.author_id,
                "commentCount":news.comments.count(),
                "collected":collected,
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
    recommend_news=[]
    sortlist = []
    news = []
    if now_news.tag:
        tag_id = now_news.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        for _news in tag.news:
            if News.query.filter_by(id=_news.news_id).first():
                if News.query.get_or_404(_news.news_id).published == 1 \
                   and _news.news_id != news_id:
                    news.append(_news.news_id)
        sortlist = sorted(news,key=lambda id: News.query.get_or_404(id).views,reverse=True)
        recommend_news = sortlist[:3] if len(sortlist)>=4 else sortlist
    return Response(json.dumps([{
            "title":News.query.get_or_404(news_id).title,
            "img_url":News.query.get_or_404(news_id).img_url,
            "author":User.query.get_or_404(News.query.get_or_404(news_id).author_id).name,
            "tag":tag.body,
            "views":News.query.get_or_404(news_id).views,
            "kind":News.query.get_or_404(news_id).kind,
            "article_id":News.query.get_or_404(news_id).id
        }for news_id in recommend_news]
    ),mimetype='application/json')

#----------------------------后台管理API---------------------------------
@api.route('/news/<int:id>/', methods=['GET'])
@admin_required
def show_news(id):
    news = News.query.get_or_404(id)
    like_degree_one = news.light.filter_by(like_degree=0).count()
    like_degree_two = news.light.filter_by(like_degree=1).count()
    like_degree_three = news.light.filter_by(like_degree=2).count()
    tagids=[pt.tag_id for pt in PostTag.query.filter_by(news_id=id).all()]
    tags=[Tag.query.filter_by(id=t).first().body for t in tagids]
    return Response(json.dumps({
        "img_url":User.query.get_or_404(news.author_id).img_url,
        "kind":1,
        "title":news.title,
        "author":User.query.get_or_404(news.author_id).name,
        "time":news.time.strftime('%Y-%m-%d'),
        "body":news.body,
        "like_degree":[like_degree_one,like_degree_two,like_degree_three],
        "editor":news.editor,
        "author_id":news.author_id,
        "commentCount":news.comments.count(),
        "tags":tags,
        }),mimetype='application/json')

@api.route('/news/', methods=["GET", "POST"])
@admin_required
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

@api.route('/news/<int:id>/', methods=["PUT"])
@admin_required
def update_news(id):
    news = News.query.get_or_404(id)
    if request.method == "PUT":
        news.title = request.get_json().get('title')
        news.author = User.query.filter_by(name=request.get_json().get('author')).first()
        news.editor = request.get_json().get('editor')
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

@api.route('/news/<int:id>/body/', methods=["GET"])
@admin_required
def get_news_body(id):
    news = News.query.get_or_404(id)
    return jsonify({
        'body':news.body
    }), 200


@api.route('/news/<int:id>/body/', methods=["PUT"])
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

@api.route('/news/<int:id>/', methods=["DELETE"])
@admin_required
def delete_news(id):
    news = News.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(news)
        db.session.commit()
        return jsonify({
            'deleted': news.id
        }), 200
 
