# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,Article,Tag
from . import api
from .. import db
from guisheng_app.decorators import admin_required
from datetime import datetime

def add_tags(article, tags, update):
    """
    判断
        向数据库中添加tag实例
        向数据库中添加tag和article关系
    """
    # add tag
    for tag in tags:
        tag_in_db = Tag.query.filter_by(body=tag).first()
        if tag_in_db:
            if (not update):
                tag_in_db.count += 1
                db.session.add(tag_in_db)
        else:
            add_tag = Tag(body=tag, count=1)
            db.session.add(add_tag)
        db.session.commit()
    # add course & tag
    for tag in tags:
        get_tag = Tag.query.filter_by(body=tag).first()
        post_tags = [t.tag_id for t in article.tag.all()]
        if get_tag.id in post_tags:
            if (not update):
                post_tag = PostTag.query.filter_by(
                    tag_id=get_tag.id, article_id=article.id,
                ).first()
                post_tag.count += 1
                db.session.add(post_tag)
        else:
            post_tag = PostTag(
                tag_id=get_tag.id, article_id=article.id, count=1
            )
            db.session.add(post_tag)
        db.session.commit()

def update_tags(article):
    """
        向数据库中更新tag实例
        向数据库中更新tag和article关系
    """
    tags = request.json.get("tags").split()
    tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
    post_tag_ids = [t.tag_id for t in article.tag.all()]
    # update tag && postTag
    for post_tag_id in post_tag_ids:
        if  post_tag_id not in tags_id:
            tag = Tag.query.filter_by(id=post_tag_id).first()
            tag.count -= 1
            db.session.add(tag)
            post_tag = PostTag.query.filter_by(
                tag_id=post_tag_id, article_id=article.id,
            ).first()
            db.session.delete(post_tag)
            db.session.commit()

@api.route('/article/<int:id>/', methods=['GET'])
def get_article(id):
    article = Article.query.get_or_404(id)
    like_degree_one = article.light.filter_by(like_degree=0).count()
    like_degree_two = article.light.filter_by(like_degree=1).count()
    like_degree_three = article.light.filter_by(like_degree=2).count()
    user_role = -1 if current_user.is_anonymous else 0
    article.views+=1
    db.session.commit()
    return Response(json.dumps({
        "kind":3,
        "title":article.title,
        "img_url":article.img_url,
        "author":User.query.get_or_404(article.author_id).name,
        "time":article.time.strftime('%Y-%m-%d'),
        "body":article.body,
        "like_degree":[like_degree_one,like_degree_two,like_degree_three],
        "commentCount":article.comments.filter_by(comment_id=-1).count(),
        "music":{
            "title":article.music_title,
            "music_url":article.music_url,
            },
        "film":{
            "film_url":article.film_url,
            },
        "editor":article.editor,
        "user_role":user_role,
        "author_id":article.author_id
        }),mimetype='application/json')

@api.route('/articles/recommend/',methods=['GET','POST'])
def recommend_articles():
    a_id = int(request.get_json().get('article_id'))
    now_a = Article.query.get_or_404(a_id)
    try:
        tag_id = now_a.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        articles = []
        for _article in tag.articles:
            articles.append(_article.article_id)
        sortlist = sorted(articles,key=lambda id: Article.query.get_or_404(id).views,reverse=True)
        recommend_articles = sortlist[:3] if len(sortlist)>=4 else sortlist
    except:
        recommend_articles=[]
    return Response(json.dumps([{
            "title":Article.query.filter_by(id=article_id).first().title,
            "description":Article.query.filter_by(id=article_id).first().description,
            "author":User.query.get_or_404(Article.query.filter_by(id=article_id).first().author_id).name,
            "tag":tag.body,
            "views":Article.query.filter_by(id=article_id).first().views
        }for article_id in recommend_articles]
    ),mimetype='application/json')

@api.route('/article/', methods=['GET','POST'])
@admin_required
def add_article():
    if request.method == "POST":
        article = Article.from_json(request.get_json())
        db.session.add(article)
        db.session.commit()
        add_tags(article, request.json.get("tags").split(), False)
        return jsonify({
            'id': article.id
        }), 201

@api.route('/article/<int:id>/', methods=["GET", "PUT"])
@admin_required
def update_article(id):
    article = Article.query.get_or_404(id)
    json = request.get_json()
    if request.method == "PUT":
        article.title = json.get('title')
        article.img_url = json.get('img_url')
        article.author = json.get('author')
        article.introduction = json.get('introduction')
        article.author =  User.query.get_or_404(json.get('author_id'))
        article.music_url = json.get('music_url')
        article.music_title = json.get('music_title')
        article.music_img_url = json.get('music_img_url')
        article.singer = json.get('singer')
        article.film_url = json.get('film_url')
        article.film_img_url = json.get('film_img_url')
        db.session.add(article)
        db.session.commit()
        add_tags(article, request.json.get("tags").split(), True)
        update_tags(article)
        return jsonify({
            'update': article.id
        }), 200

@api.route('/article/<int:id>/body/', methods=["GET", "PUT"])
@admin_required
def update_article_body(id):
    article = Article.query.get_or_404(id)
    if request.method == "PUT":
        article.body = request.get_json().get('body')
        db.session.add(article)
        db.session.commit()
        return jsonify({
            'update': article.id
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

