# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,Article,Tag,PostTag,Collect
from . import api
from .. import db
from guisheng_app.decorators import admin_required
from datetime import datetime

@api.route('/article/<int:id>/', methods=['POST'])
def get_article(id):
    if request.method == 'POST':
        my_id = int(request.get_json().get('my_id'))
        article = Article.query.get_or_404(id)
        if article.published == 1:
            like_degree_one = article.light.filter_by(like_degree=0).count()
            like_degree_two = article.light.filter_by(like_degree=1).count()
            like_degree_three = article.light.filter_by(like_degree=2).count()
            article.views+=1
            db.session.commit()
            if my_id == -1:
                collected=0
            else:
                if Collect.query.filter_by(article_id=id).filter_by(author_id=my_id).first():
                    collected=1
                else:
                    collected=0
            return Response(json.dumps({
                "kind":3,
                "title":article.title,
                "img_url":User.query.get_or_404(article.author_id).img_url,
                "author":User.query.get_or_404(article.author_id).name,
                "time":article.time.strftime('%Y-%m-%d'),
                "body":article.body_html,
                "like_degree":[like_degree_one,like_degree_two,like_degree_three],
                "commentCount":article.comments.count(),
                "music":{
                    "title":article.music_title,
                    "music_url":article.music_url,
                    "singer":article.singer,
                    "music_img_url":article.music_img_url
                    },
                "film":{
                    "film_url":article.film_url,
                    "scores":article.scores,
                    "film_img_url":article.film_img_url
                    },
                "editor":article.editor,
                "author_id":article.author_id,
                "collected":collected
                }),mimetype='application/json')

@api.route('/article/recommend/',methods=['GET','POST'])
def recommend_articles():
    a_id = int(request.get_json().get('article_id'))
    now_a = Article.query.get_or_404(a_id)
    recommend_articles=[]
    sortlist = []
    articles = []
    if now_a.tag:
        tag_id = now_a.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        for _article in tag.articles:
            if Article.query.filter_by(id=_article.article_id).first():
                if Article.query.get_or_404(_article.article_id).published == 1 \
                   and _article.article_id != a_id:
                    articles.append(_article.article_id)
        sortlist = sorted(articles,key=lambda id: Article.query.get_or_404(id).views,reverse=True)
        recommend_articles = sortlist[:3] if len(sortlist)>=4 else sortlist
    return Response(json.dumps([{
            "title":Article.query.get_or_404(article_id).title,
            "description":Article.query.get_or_404(article_id).description,
            "author":User.query.get_or_404(Article.query.get_or_404(article_id).author_id).name,
            "tag":tag.body,
            "views":Article.query.get_or_404(article_id).views,
            "kind":Article.query.get_or_404(article_id).kind,
            "article_id":Article.query.get_or_404(article_id).id
        }for article_id in recommend_articles]
    ),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
@api.route('/article/<int:id>/', methods=['GET'])
@admin_required
def show_article(id):
    article = Article.query.get_or_404(id)
    like_degree_one = article.light.filter_by(like_degree=0).count()
    like_degree_two = article.light.filter_by(like_degree=1).count()
    like_degree_three = article.light.filter_by(like_degree=2).count()
    tagids=[pt.tag_id for pt in PostTag.query.filter_by(article_id=id).all()]
    tags=[Tag.query.filter_by(id=t).first().body for t in tagids]
    return Response(json.dumps({
        "kind":3,
        "title":article.title,
        "img_url":User.query.get_or_404(article.author_id).img_url,
        "author":User.query.get_or_404(article.author_id).name,
        "time":article.time.strftime('%Y-%m-%d'),
        "body":article.body_html,
        "like_degree":[like_degree_one,like_degree_two,like_degree_three],
        "commentCount":article.comments.count(),
        "tags":tags,
        "music_title":article.music_title,
        "music_url":article.music_url,
        "singer":article.singer,
        "music_img_url":article.music_img_url,
        "film_url":article.film_url,
        "scores":article.scores,
        "film_img_url":article.film_img_url,
        "editor":article.editor,
        "author_id":article.author_id,
        "description":article.description
        }),mimetype='application/json')

@api.route('/article/',methods=['POST'])
@admin_required
def add_article():
    if request.method == 'POST':
        article = Article.from_json(request.get_json())
        db.session.add(article)
        db.session.commit()
        tags = request.get_json().get('tags')
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            article_tags = [t.tag_id for t in article.tag.all()]
            if get_tag.id not in article_tags:
                post_tag = PostTag(article_tags=get_tag,articles=article)
                db.session.add(post_tag)
                db.session.commit()
        return jsonify({
            'id':article.id
        }), 201

@api.route('/article/<int:id>/',methods=['PUT'])
@admin_required
def update_article(id):
    article = Article.query.get_or_404(id)
    if request.method == 'PUT':
        article.title = request.get_json().get('title')
        article.img_url = request.get_json().get('img_url')
        article.author = User.query.filter_by(name=request.get_json().get('author')).first()
        article.description = request.get_json().get('description')
        article.music_url = request.get_json().get('music_url')
        article.music_title = request.get_json().get('music_title')
        article.music_img_url = request.get_json().get('music_img_url')
        article.singer = request.get_json().get('singer')
        article.film_url = request.get_json().get('film_url')
        article.film_img_url = request.get_json().get('film_img_url')
        article.editor = request.get_json().get('editor')
        article.scores = request.get_json().get('scores')
        db.session.add(article)
        db.session.commit()

        tags = request.get_json().get('tags')
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            article_tags = [t.tag_id for t in article.tag.all()]
            if get_tag.id not in article_tags:
                post_tag = PostTag(article_tags=get_tag,articles=article)
                db.session.add(post_tag)
                db.session.commit()

        tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
        article_tag_ids = [t.tag_id for t in article.tag.all()]
        for article_tag_id in article_tag_ids:
            if  article_tag_id not in tags_id:
                a_tag = Tag.query.get_or_404(article_tag_id)
                post_tag = PostTag.query.filter_by(article_tags=a_tag,articles=article).first()
                db.session.delete(post_tag)
                db.session.commit()

        return jsonify({
            'update': article.id
        }),200

@api.route('/article/<int:id>/body/', methods=["GET"])
@admin_required
def get_article_body(id):
    article = Article.query.get_or_404(id)
    return jsonify({
        "body":article.body
    })

@api.route('/article/<int:id>/body/', methods=["PUT"])
@admin_required
def update_article_body(id):
    article = Article.query.get_or_404(id)
    if request.method == "PUT":
        article.body = request.get_json().get('body')
        db.session.add(article)
        db.session.commit()
        return jsonify({
            'update':article.id
        }), 200

@api.route('/article/<int:id>/', methods=["GET", "DELETE"])
@admin_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(article)
        db.session.commit()
        return jsonify({
            'deleted': article.id
        }), 200

