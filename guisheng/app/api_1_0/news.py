# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,PostTag,Tag
from . import api


@api.route('/news/<int:id>', methods=['GET'])
def get_news(id):
    news = News.query.get_or_404(id)
    return Response(json.dumps({
        "title":news.title,
        "author":User.query.get_or_404(news.author_id).name,
        "time":news.time.strftime('%m/%d/%Y'),
        "body":news.body,
        }),mimetype='application/json')

@api.route('/news', methods=['GET','POST'])
def command_news():
    news_id = int(request.get_json().get('article_id'))
    now_news = News.query.get_or_404(n_id)
    tag_id = now_news.tag[0].tag_id
    tag = Tag.query.get_or_404(tag_id)
    news = []
    for _news in tag.news:
        news.append(_news.news_id)
    sortlist = sorted(news,key=lambda id: News.query.get_or_404(id).views,reverse=True)
    command_news = sortlist[:3]
    return Response(json.dumps([{
            "title":News.query.get_or_404(news_id).title,
            "description":News.query.get_or_404(news_id).description,
            "author":User.query.get_or_404(News.query.get_or_404(news_id).author_id).name,
            "tag":tag.body,
             "views":News.query.get_or_404(news_id).views
        }for news_id in command_news]
    ),mimetype='application/json')

 
