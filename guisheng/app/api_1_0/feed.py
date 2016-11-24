# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api

@api.route('/feed/', methods=['GET','POST'])
def main_page():
    kind = int(request.args.get('kind'))
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))

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
        tolist.sort()
        return Response(json.dumps([{
                "kind":kind,
                "article_id":content.id,
                "img_url":content.img_url,
                "title":content.title,
                "author":User.query.get_or_404(content.author_id).name,
                "views":content.views,
                "tag":content.tag,
                "description":content.description,
                "time":content.time.strftime('%Y-%m-%d %H:%M:%S %f'),
                } for content in tolist[:count-1]]
        ),mimetype='application/json')

    elif kind == 1:
        news = News.query.order_by(News.time.desc()).limit(count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":singlenews.id,
                "img_url":singlenews.img_url,
                "title":singlenews.title,
                "author":User.query.get_or_404(singlenews.author_id).name,
                "views":singlenews.views,
                "tag":singlenews.tag,
                "description":singlenews.description,
                "time":singlenews.time.strftime('%Y-%m-%d %H:%M:%S %f'),
            } for singlenews in news]
        ),mimetype='application/json')

    elif kind == 2:
        pictures = Picture.query.order_by(Picture.time.desc()).limit(count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":picture.id,
                "img_url":picture.img_url,
                "title":picture.title,
                "author":User.query.get_or_404(picture.author_id).name,
                "views":picture.views,
                "tag":picture.tag,
                "description":picture.description,
            }for picture in pictures]
        ),mimetype='application/json')


    elif kind == 3:
        articles = Article.query.order_by(Article.time.desc()).limit(count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":article.id,
                "img_url":article.img_url,
                "title":article.title,
                "author":User.query.get_or_404(article.author_id).name,
                "views":article.views,
                "tag":article.tag,
                "description":article.description,
            }for article in articles]
        ),mimetype='application/json')

    else:
        interactions = Interaction.query.order_by(Interaction.time.desc()).limit(count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":interaction.id,
                "img_url":interaction.img_url,
                "title":interaction.title,
                "author":User.query.get_or_404(interaction.author_id).name,
                "views":interaction.views,
                "tag":interaction.tag,
                "description":interaction.description,
            }for interaction in interactions]
        ),mimetype='application/json')
