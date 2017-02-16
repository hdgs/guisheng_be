# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,News,PostTag,Tag
from . import api
from .. import db
from guisheng_app.decorators import admin_required

def add_tags(news, tags, update):
    """
    判断
        向数据库中添加tag实例
        向数据库中添加tag和news关系
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
        post_tags = [t.tag_id for t in news.tag.all()]
        if get_tag.id in post_tags:
            if (not update):
                post_tag = PostTag.query.filter_by(
                    tag_id=get_tag.id, news_id=news.id,
                ).first()
                post_tag.count += 1
                db.session.add(post_tag)
        else:
            post_tag = PostTag(
                tag_id=get_tag.id, news_id=news.id, count=1
            )
            db.session.add(post_tag)
        db.session.commit()

def update_tags(news):
    """
        向数据库中更新tag实例
        向数据库中更新tag和news关系
    """
    tags = request.json.get("tags").split()
    tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
    post_tag_ids = [t.tag_id for t in news.tag.all()]
    # update tag && postTag
    for post_tag_id in post_tag_ids:
        if  post_tag_id not in tags_id:
            tag = Tag.query.filter_by(id=post_tag_id).first()
            tag.count -= 1
            db.session.add(tag)
            post_tag = PostTag.query.filter_by(
                tag_id=post_tag_id, news_id=news.id,
            ).first()
            db.session.delete(post_tag)
            db.session.commit()

@api.route('/news/<int:id>/', methods=['GET'])
def get_news(id):
    news = News.query.get_or_404(id)
    like_degree_one = news.light.filter_by(like_degree=0).count()
    like_degree_two = news.light.filter_by(like_degree=1).count()
    like_degree_three = news.light.filter_by(like_degree=2).count()
    user_role=-1 if current_user.is_anonymous else 0
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
        "user_role":user_role,
        "author_id":news.author_id
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

@api.route('/news/', methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "POST":
        news = News.from_json(request.get_json())
        db.session.add(news)
        db.session.commit()
        add_tags(news, request.json.get("tags").split(), False)
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
        add_tags(news, request.json.get("tags").split(), True)
        update_tags(news)
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
 
