# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api
from operator import attrgetter

@api.route('/feed/', methods=['GET','POST'])
def main_page():
    if request.method == 'GET':
        kind = request.args.get('kind',type=int)
        page = request.args.get('page',type=int)
        count = request.args.get('count',type=int)

        if kind == 0:
            tolist = []
            for n in News.query.order_by(News.time.desc()).limit(count):
                tolist.append(n)
            for p in Picture.query.order_by(Picture.time.desc()).limit(count):
                tolist.append(p)
            for a in Article.query.order_by(Article.time.desc()).limit(count):
                tolist.append(a)
            for i in Interaction.query.order_by(Interaction.time.desc()).limit(count):
                tolist.append(i)
            tolist.sort(key=attrgetter('time'),reverse=True)
            return Response(json.dumps([{
                    "kind":kind,
                    "article_id":content.id,
                    "img_url":content.img_url[0],
                    "title":content.title,
                    "author":User.query.get_or_404(content.author_id).name,
                    "views":content.views,
                    "tag":content.tag[0],
                    "description":content.description,
                    "time":content.time.strftime('%m/%d/%Y'),
                    } for content in tolist[:count-1]]
            ),mimetype='application/json')

        elif kind == 1:
            news = News.query.order_by(News.time.desc()).limit(count)
            return Response(json.dumps([{
                    "kind":kind,
                    "article_id":singlenews.id,
                    "img_url":singlenews.img_url[0],
                    "title":singlenews.title,
                    "author":User.query.get_or_404(singlenews.author_id).name,
                    "views":singlenews.views,
                    "tag":singlenews.tag[0],
                    "description":singlenews.description,
                } for singlenews in news]
            ),mimetype='application/json')

        elif kind == 2:
            pictures = Picture.query.order_by(Picture.time.desc()).limit(count)
            return Response(json.dumps([{
                    "kind":kind,
                    "article_id":picture.id,
                    "img_url":picture.img_url[0],
                    "title":picture.title,
                    "author":User.query.get_or_404(picture.author_id).name,
                    "views":picture.views,
                    "tag":picture.tag[0],
                    "description":picture.description,
                }for picture in pictures]
            ),mimetype='application/json')


        elif kind == 3:
            articles = Article.query.order_by(Article.time.desc()).limit(count)
            return Response(json.dumps([{
                    "kind":kind,
                    "article_id":article.id,
                    "img_url":article.img_url[0],
                    "title":article.title,
                    "author":User.query.get_or_404(article.author_id).name,
                    "views":article.views,
                    "tag":article.tag[0],
                    "description":article.description,
                }for article in articles]
            ),mimetype='application/json')

        else:
            interactions = Interaction.query.order_by(Interaction.time.desc()).limit(count)
            return Response(json.dumps([{
                    "kind":kind,
                    "article_id":interaction.id,
                    "img_url":interaction.img_url[0],
                    "title":interaction.title,
                    "author":User.query.get_or_404(interaction.author_id).name,
                    "views":interaction.views,
                    "tag":interaction.tag,
                    "description":interaction.description,
                }for interaction in interactions]
            ),mimetype='application/json')

    if request.method == 'POST':
        #        count = request.args.get('count',type=int)
        content = request.get_json().get("content")
        alist = []
        for n in News.query.order_by(News.time.desc()).all():
            if n.title==content or content in n.tag:
                alist.append(n)
        for p in Picture.query.order_by(Picture.time.desc()).all():
            if p.title==content or content in p.tag:
                alist.append(p)
        for a in Article.query.order_by(Article.time.desc()).all():
            if a.title==content or content in a.tag:
                alist.append(a)
        for i in Interaction.query.order_by(Interaction.time.desc()).all():
            if i.title==content or content in i.tag:
                alist.append(i)
        alist.sort(key=attrgetter('time'),reverse=True)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":content.id,
                "img_url":content.img_url[0],
                "title":content.title,
                "author":User.query.get_or_404(content.author_id).name,
                "views":content.views,
                "tag":content.tag[0],
                "description":content.description,
                "time":content.time.strftime('%m/%d/%Y'),
                } for content in alist[:count-1]]
        ),mimetype='application/json')

