# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,PostTag,Tag
from . import api


@api.route('/news/<int:id>', methods=['GET'])
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


@api.route('/news/', methods=['GET','POST'])
def command_news():
    news_id = int(request.get_json().get('article_id'))
    now_news = News.query.get_or_404(news_id)
    try:
        tag_id = now_news.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        news = []
        for _news in tag.news:
            news.append(_news.news_id)
        sortlist = sorted(news,key=lambda id: News.query.get_or_404(id).views,reverse=True)
        command_news = sortlist[:3] if len(sortlist)>=4 else sortlist
    except:
        command_news=[]
    return Response(json.dumps([{
            "title":News.query.filter_by(id=news_id).first().title,
            "description":News.query.filter_by(id=news_id).first().description,
            "author":User.query.get_or_404(News.query.filter_by(id=news_id).first().author_id).name,
            "tag":tag.body,
            "views":News.query.filter_by(id=news_id).first().views
        }for news_id in command_news]
    ),mimetype='application/json')

 
