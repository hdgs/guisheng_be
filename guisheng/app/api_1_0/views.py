# coding: utf-8
from flask import render_template,jsonify,Response,g
import json
from ..models import News,Picture,Article,Interaction
from . import api

@api.route('/feed/', methods=['GET','POST'])
def main_page():
    kind = request.args.get('kind')
    page = request.args.get('page')
    count = request.args.get('count')

    if kind == 0:
        news = News.query.order_by(News.time.desc()).limit(count)
        pictures = Picture.query.order_by(Picture.time.desc()).limit(count)
        articles = Article.query.order_by(Article.time.desc()).limit(count)
        interactions = Interaction.query.order_by(Interaction.time.desc()).limit(count)
        tolist = []
        for n in news:
            tolist.append(n)
        for p in pictures:
            tolist.append(p)
        for a in articles:
            tolist.append(a)
        for i in interactions:
            tolist.append(i)
        tolist.sort(reverse=True)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":content.id,
                "img_url":content.img_url,
                "title":content.title,
                "author":content.author,
                "views":content.views,
                "tag":content.tag,
                "description":content.description,
            } for content in tolist]
        ),mimetype='application/json')

    if kind == 1:
        news = News.query.order_by(News.time.desc()).limit(count).offset((page-1)*count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":singlenews.id,
                "img_url":singlenews.img_url,
                "title":singlenews.title,
                "author":singlenews.author,
                "views":singlenews.views,
                "tag":singlenews.tag,
                "description":singlenews.description,
            }for singlenews in news]
        ),mimetype='application/json')

    if kind == 2:
        pictures = Picture.query.order_by(Picture.time.desc()).limit(count).offset((page-1)*count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":picture.id,
                "img_url":picture.img_url,
                "title":picture.title,
                "author":picture.author,
                "views":picture.views,
                "tag":picture.tag,
                "description":picture.description,
            }for picture in pictures]
        ),mimetype='application/json')


    if kind == 3:
        articles = Article.query.order_by(Article.time.desc()).limit(count).offset((page-1)*count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":article.id,
                "img_url":article.img_url,
                "title":article.title,
                "author":article.author,
                "views":article.views,
                "tag":article.tag,
                "description":article.description,
            }for article in articles]
        ),mimetype='application/json')

    if kind == 4:
        interactions = Interaction.query.order_by(Interaction.time.desc()).limit(count).offset((page-1)*count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":interaction.id,
                "img_url":interaction.img_url,
                "title":interaction.title,
                "author":interaction.author,
                "views":interaction.views,
                "tag":interaction.tag,
                "description":interaction.description,
            }for interaction in interactions]
        ),mimetype='application/json')

@api.route('/everydaypic/', methods=['GET','POST'])
def get_everydaypic():
    everydaypic = Everydaypic.query.first()
    return Response(json.dumps({
        "img_url":everydaypic.img_url,
        "temperature":everydaypic.temperature,
        "date":everydaypic.date,
        "place":everydaypic.place,
        }),mimetype='application/json')

@api.route('/pics/<int:id>/', methods=['GET','POST'])
def get_pic(id):
    pic = Picture.query.get_or_404(id)
    return Response(json.dumps({
        "title":pic.title,
        "author":pic.author,
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
            "author":photo.author,
            "views":photo.views,
            "tag":photo.tag,
        } for photo in photos]
    ),mimetype='application/json')
        
@api.route('/news/<int:id>/', methods=['GET','POST'])
def get_news(id):
    news = News.query.get_or_404(id)
    return Response(json.dumps({
        "title":news.title,
        "author":news.author,
        "time":news.time.strftime('%Y-%m-%d %H:%M:%S %f'),
        "body":news.body,
        }),mimetype='application/json')

@api.route('/article/<int:id>/', methods=['GET','POST'])
def get_article(id):
    article = Article.query.get_or_404(id)
    return Response(json.dumps({
        "title":article.title,
        "img_url":article.img_url,
        "author":article.author,
        "time":article.time.strftime('%Y-%m-%d %H:%M:%S %f'),
        "body":article.body,
        "music":{
            "title":article.music_title,
            "music_url":article.music_url,
            },
        "film":{
            "film_url":article.film_url,
            }
        }),mimetype='application/json')

@api.route('/interaction/<int:id>/',methods=['GET'])
def get_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    return Response(json.dumps({
        "title":interaction.title,
        "author":interaction.author,
        "time":interaction.time.strftime('%Y-%m-%d %H:%M:%S %f'),
        "body":interaction.body,
        }),mimetype='application/json')

@api.route('/profile/<int:id>/', methods=['GET','POST','PUT'])
def profile(id):
    if request.method == 'GET':
        user = User.query.get_or_404(id)
        return Response(json.dumps({
            "img_url":user.img_url,
            "name":user.name,
            "weibo":user.weibo,
            "introduction":user.introduction,
            "works":user.works,
            "collection":user.collection,
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
            "works":user.works,
            "collection":user.collection,
            "suggestion":user.suggestion,
            }),mimetype='application/json')


@api.route('/comments/',methods=['GET','POST'])
def comments():
    if request.method == 'GET':
        kind = request.args.get('kind')
        article_id = request.args.get('article_id')
        if kind == 1:
            post = News.query.get_or_404(article_id)
        if kind == 2:
            post = Picture.query.get_or_404(article_id)
        if kind == 3:
            post = Article.query.get_or_404(article_id)
        if kind == 4:
            post = Interaction.query.get_or_404(article_id)
        comments = post.comments.order_by(Comment.time.asc()).items
        return Response(json.dumps([{
                "article_id":article_id,
                "img_url":g.current_user.img_url,
                "message":comment.body,
                "comments":[],
                "likes":comment.likes,
            } for comment in comments]
        ),mimetype='application/json')

    if request.method == 'POST':
        comment = Comment()
        kind = request.get_json().get("kind")
        if kind == 1:
            comment.news_id = request.get_json().get("article_id")
        if kind == 2:
            comment.picture_id = request.get_json.get("article_id")
        if kind == 3:
            comment.article_id = request.get_json.get("article_id")
        if kind == 4:
            comment.interaction_id = request.get_json.get("article_id")
        comment.id = request.get_json().get("comment_id")
        comment.body = request.get_json().get("message")
        comment.author_id = request.get_json().get("user_id")
        db.session.add(comment)
        db.session.commit()
        return Response(json.dumps({
            "status":"200",
            }),mimetype='application/json')

@api.route('/comments/<int:id>/like/')
def get_comment_likes(id):
    comment = Comment.query.get_or_404(id)
    likes = comment.like.count() 
    return Response(json.dumps({
        "likes":likes,
        }),mimetype='application/json')

@api.route('/light/',methods=['GET','POST'])
def light():
    light = Light()
    light.like_degree = request.get_json().get("like_degree")
    kind = request.get_json().get("kind")
    if kind == 1:
        light.news_id = request.get_json().get("article_id") 
    if kind == 2:
        light.picture_id = request.get_json().get("article_id")
    if kind == 3:
        light.article_id = request.get_json().get("article_id")
    if kind == 4:
        light.interaction_id = request.get_json().get("article_id")
    db.session.add(light)
    db.session.commit()
 
