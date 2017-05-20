# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment,PostTag,Tag
from . import api
from operator import attrgetter
from guisheng_app import rds
from .. import db
from guisheng_app.decorators import admin_required

@api.route('/feed/', methods=['GET'])
def main_page():
    kind = int(request.args.get('kind'))
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    if kind == 0:
        tolist = []
        for n in News.query.filter_by(published=1).filter_by(tea=0).order_by(News.time.desc()).limit(count):
            tolist.append(n)
        for p in Picture.query.filter_by(published=1).filter_by(tea=0).order_by(Picture.time.desc()).limit(count):
            tolist.append(p)
        for a in Article.query.filter_by(published=1).filter_by(tea=0).order_by(Article.time.desc()).limit(count):
            tolist.append(a)
        for i in Interaction.query.filter_by(published=1).filter_by(tea=0).order_by(Interaction.time.desc()).limit(count):
            tolist.append(i)
        tolist.sort(key=attrgetter('time'),reverse=True)
        return Response(json.dumps([{
                "kind":content.kind,
                "article_id":content.id,
                "img_url":content.img_url if content.__class__!=Picture \
                          else [i for i in content.img_url][0].img_url if [i for i in content.img_url]\
                          else "",
                "title":content.title,
                "author":User.query.get_or_404(content.author_id).name if content.author_id else None,
                "views":content.views,
                "tag":Tag.query.get_or_404(content.__class__.query.get_or_404(content.id).tag[0].tag_id).body\
                      if len([i for i in content.__class__.query.get_or_404(content.id).tag]) else "",
                "tags":[Tag.query.get_or_404(t.tag_id).body for t in content.__class__.query.get_or_404(content.id).tag]\
                       if len([i for i in content.__class__.query.get_or_404(content.id).tag]) else [""],
                "time":content.time.strftime('%Y-%m-%d'),
                "description":content.description
                } for content in tolist[:count]]
        ),mimetype='application/json')
    else:
        post_kind = {1: News, 2: Picture, 3: Article, 4: Interaction}.get(kind)
        posts = post_kind.query.filter_by(published=1).filter_by(tea=0).order_by(post_kind.time.desc()).limit(count)
        return Response(json.dumps([{
                "kind":kind,
                "article_id":_post.id,
                "img_url":_post.img_url if _post.__class__!=Picture \
                          else [i for i in _post.img_url][0].img_url if [i for i in _post.img_url]\
                          else "",
                "title":_post.title,
                "author":User.query.get_or_404(_post.author_id).name if _post.author_id else None,
                "views":_post.views,
                "tag":Tag.query.get_or_404(post_kind.query.get_or_404(_post.id).tag[0].tag_id).body\
                      if len([i for i in post_kind.query.get_or_404(_post.id).tag]) else "",
                "tags":[Tag.query.get_or_404(t.tag_id).body for t in post_kind.query.get_or_404(_post.id).tag]\
                       if len([i for i in post_kind.query.get_or_404(_post.id).tag]) else [""],
                "time":_post.time.strftime('%Y-%m-%d'),
                "description":_post.description,
                "published":_post.published,
                "count":post_kind.query.count()
            } for _post in posts],
        ),mimetype='application/json')

@api.route('/feed/', methods=['POST'])
def search():
    if request.method == 'POST':
        content = request.get_json().get("content")
        #存储热门标签
        if Tag.query.filter_by(body=content).first():
            if rds.get(content) is None:
                rds.set(content, 1)
            else:
                rds.incr(content)
        rds.save()
        #返回搜索结果
        alist = []
        for n in News.query.whoosh_search(content):
            if n.published == 1:
                alist.append(n)
        for p in Picture.query.whoosh_search(content):
            if n.published == 1:
                alist.append(p)
        for a in Article.query.whoosh_search(content):
            if n.published == 1:
                alist.append(a)
        for i in Interaction.query.whoosh_search(content):
            if n.published == 1:
                alist.append(i)
        for t in Tag.query.filter_by(body=content).all():
            for _news in t.news:
                if News.query.filter_by(id=_news.news_id).first():
                    if News.query.get_or_404(_news.news_id).published == 1:
                        alist.append(News.query.get_or_404(_news.news_id))
            for _article in t.articles:
                if Article.query.filter_by(id=_article.article_id).first():
                    if Article.query.get_or_404(_article.article_id).published == 1:
                        alist.append(Article.query.get_or_404(_article.article_id))
            for _pic in t.pictures:
                if Picture.query.filter_by(id=_pic.picture_id).first():
                    if Picture.query.get_or_404(_pic.picture_id).published == 1:
                        alist.append(Picture.query.get_or_404(_pic.picture_id))
            for _interaction in t.interactions:
                if Interaction.query.filter_by(id=_interaction.interaction_id).first():
                    if Interaction.query.get_or_404(_interaction.interaction_id).published == 1:
                        alist.append(Interaction.query.get_or_404(_interaction.interaction_id))
        return Response(json.dumps([{
                "kind":post.kind,
                "article_id":post.id,
                "img_url":post.img_url if post.__class__!=Picture \
                         else [i for i in post.img_url][0].img_url,
                "title":post.title,
                "author":User.query.get_or_404(post.author_id).name if post.author_id else None,
                "views":post.views,
                "description":post.description,
                "time":post.time.strftime('%Y-%m-%d'),
                "tag":Tag.query.get_or_404(post.__class__.query.get_or_404(post.id).tag[0].tag_id).body\
                      if len([i for i in post.__class__.query.get_or_404(post.id).tag]) else "",
                "tags":[Tag.query.get_or_404(t.tag_id).body for t in post.__class__.query.get_or_404(post.id).tag]\
                      if len([i for i in post.__class__.query.get_or_404(post.id).tag]) else [""], 
                } for post in alist[:9]]
        ),mimetype='application/json')

@api.route('/hottag/',methods=['GET'])
def get_hottag():
    tags = rds.keys()
    hot_tags = sorted(tags, key=lambda w: int(rds.get(w)), reverse=True)[:10]
    return Response(json.dumps({
        "hot_tag":hot_tags
    }),mimetype='application/json')

#----------------------------后台管理API---------------------------------
@api.route('/list/', methods=['GET'])
@admin_required
def list():
    kind = int(request.args.get('kind'))
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    post_kind = {1: News, 2: Picture, 3: Article, 4: Interaction}.get(kind)
    posts=[]
    if kind in [3,4]:
        flag = int(request.args.get('flag'))
        posts = post_kind.query.filter_by(flag=flag).order_by(post_kind.time.desc()).limit(count).offset((page-1)*count)
    else:
        posts = post_kind.query.order_by(post_kind.time.desc()).limit(count).offset((page-1)*count)
    return Response(json.dumps([{
            "kind":kind,
            "article_id":_post.id,
            "img_url":_post.img_url if _post.__class__!=Picture \
                      else [i for i in _post.img_url][0].img_url if [i for i in _post.img_url]\
                      else "",
            "title":_post.title,
            "author":User.query.get_or_404(_post.author_id).name if _post.author_id else None,
            "views":_post.views,
            "tag":Tag.query.get_or_404(post_kind.query.get_or_404(_post.id).tag[0].tag_id).body\
                  if len([i for i in post_kind.query.get_or_404(_post.id).tag]) else "",
            "tags":[Tag.query.get_or_404(t.tag_id).body for t in post_kind.query.get_or_404(_post.id).tag]\
                   if len([i for i in post_kind.query.get_or_404(_post.id).tag]) else [""],
            "time":_post.time.strftime('%Y-%m-%d'),
            "description":_post.description,
            "published":_post.published,
            "count":post_kind.query.filter_by(flag=flag).count() if kind in [3,4] else post_kind.query.count(),
            "tea":_post.tea
        } for _post in posts],
    ),mimetype='application/json')

@api.route('/publish/', methods=['POST'])
@admin_required
def publish():
    if request.method == 'POST':
        kind = int(request.get_json().get("kind"))
        post_id = int(request.get_json().get("post_id"))
        if kind == 1:
            post = News.query.get_or_404(post_id)
        if kind == 2:
            post = Picture.query.get_or_404(post_id)
        if kind == 3:
            post = Article.query.get_or_404(post_id)
        if kind == 4:
            post = Interaction.query.get_or_404(post_id)
        post.published = 1
        db.session.add(post)
        db.session.commit()
        return jsonify({
                "published":post.id
            })

@api.route('/unpublish/', methods=['POST'])
@admin_required
def unpublish():
    if request.method == 'POST':
        kind = int(request.get_json().get("kind"))
        post_id = int(request.get_json().get("post_id"))
        if kind == 1:
            post = News.query.get_or_404(post_id)
        if kind == 2:
            post = Picture.query.get_or_404(post_id)
        if kind == 3:
            post = Article.query.get_or_404(post_id)
        if kind == 4:
            post = Interaction.query.get_or_404(post_id)
        post.published = 0
        db.session.add(post)
        db.session.commit()
        return jsonify({
                "unpublished":post.id
            })

