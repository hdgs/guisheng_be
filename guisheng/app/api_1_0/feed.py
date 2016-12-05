# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api
from operator import attrgetter

@api.route('/feed/', methods=['GET'])
def main_page():
    kind = int(request.args.get('kind')
    page = int(request.args.get('page')
    count = int(request.args.get('count')
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
                "tag":Tag.query.get_or_404(content.__class__.query.get_or_404(content.id).tag[0].tag_id)
                "description":content.description,
                } for content in tolist[:count-1]]
        ),mimetype='application/json')
    else:
        post_kind = {1: News, 2: Picture, 3: Article, 4: Interaction}.get(kind)
        posts = post_kind.query.order_by(post_kind.time.desc()).limit(count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":_post.id,
                "img_url":_post.img_url[0],
                "title":_post.title,
                "author":User.query.get_or_404(_post.author_id).name,
                "views":_post.views,
                "tag":Tag.query.get_or_404(post_kind.query.get_or_404(content.id).tag[0].tag_id)
                "description":_post.description,
            } for _post in posts]
        ),mimetype='application/json')

@api.route('/feed/', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        count = int(request.args.get('count')
        content = int(request.get_json().get("content"))
        alist = []
        for n in News.query.order_by(News.time.desc()).all():
            if n.title==content:
                alist.append(n)
        for p in Picture.query.order_by(Picture.time.desc()).all():
            if p.title==content:
                alist.append(p)
        for a in Article.query.order_by(Article.time.desc()).all():
            if a.title==content:
                alist.append(a)
        for i in Interaction.query.order_by(Interaction.time.desc()).all():
            if i.title==content:
                alist.append(i)
        for t in Tag.query.order_by(Tag.time.desc()).all():
            if t.body==content:
                for _news in tag.news:
                    alist.append(_news)
                for _article in tag.articles:
                    alist.append(_article)
                for _pic in tag.pictures:
                    alist.append(_pic)
                for _interaction in tag.interactions:
                    alist.append(_article)
        alist.sort(key=attrgetter('time'),reverse=True)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":content.id,
                "img_url":content.img_url[0],
                "title":content.title,
                "author":User.query.get_or_404(content.author_id).name,
                "views":content.views,
                # "tag":content.tag[0],
                "description":content.description,
                "time":content.time.strftime('%m/%d/%Y'),
                } for content in alist[:count-1]]
        ),mimetype='application/json')

