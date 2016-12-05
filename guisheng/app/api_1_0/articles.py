# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,Article
from . import api


@api.route('/article/<int:id>/', methods=['GET'])
def get_article(id):
    article = Article.query.get_or_404(id)
    return Response(json.dumps({
        "title":article.title,
        "img_url":article.img_url,
        "author":User.query.get_or_404(article.author_id).name,
        "time":article.time.strftime('%m/%d/%Y'),
        "body":article.body,
        "music":{
            "title":article.music_title,
            "music_url":article.music_url,
            },
        "film":{
            "film_url":article.film_url,
            }
        }),mimetype='application/json')

@api.route('/articles/',methods=['GET','POST'])
def command_articles():
    a_id = int(request.get_json().get('article_id'))
    now_a = Article.query.get_or_404(a_id)
    tag_id = now_a.tag[0].tag_id
    tag = Tag.query.get_404(tag_id)
    articles = []
    for _article in tag.articles:
        articles.append(_article.article_id)
    sortlist = sorted(articles,key=lambda id: Article.query.get_or_404(id).views,reverse=True)
    command_articles = sortlist[:3]
    return Response(json.dumps([{
            "title":article.title,
            "description":article.description,
            "author":User.query.get_or_404(article.author_id).name,
            "tag":tag.body,
            "views":article.views
        }for article in command_articles]
    ),mimetype='application/json')


