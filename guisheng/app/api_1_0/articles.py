# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,Article,Tag
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
    try:
        tag_id = now_a.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        articles = []
        for _article in tag.articles:
            articles.append(_article.article_id)
        sortlist = sorted(articles,key=lambda id: Article.query.get_or_404(id).views,reverse=True)
        command_articles = sortlist[:3] if len(sortlist)>=4 else sortlist
    except:
        command_articles=[]
    return Response(json.dumps([{
            "title":Article.query.filter_by(id=article_id).first().title,
            "description":Article.query.filter_by(id=article_id).first().description,
            "author":User.query.get_or_404(Article.query.filter_by(id=article_id).first().author_id).name,
            "tag":tag.body,
            "views":Article.query.filter_by(id=article_id).first().views
        }for article_id in command_articles]
    ),mimetype='application/json')


