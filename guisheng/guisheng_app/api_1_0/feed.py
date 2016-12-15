# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment,PostTag,Tag
from . import api
from operator import attrgetter
from guisheng_app import rds


@api.route('/feed/', methods=['GET'])
def main_page():
    kind = int(request.args.get('kind'))
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
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
                "tag":Tag.query.get_or_404(content.__class__.query.get_or_404(content.id).tag[0].tag_id).body\
                      if len([i for i in content.__class__.query.get_or_404(content.id).tag]) else "",
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
                "tag":Tag.query.get_or_404(post_kind.query.get_or_404(content.id).tag[0].tag_id).body\
                      if len([i for i in post_kind.query.get_or_404(content.id).tag]) else "",
                "description":_post.description,
            } for _post in posts]
        ),mimetype='application/json')


@api.route('/feed/', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        count = int(request.args.get('count'))
        content = request.get_json().get("content")
        #存储热门标签
        if Tag.query.filter_by(body=content).first():
            if rds.get(content) is None:
                rds.set(content, 1)
            else:
                rds.incr(content)
        #返回搜索结果
        alist = []
        for n in News.query.whoosh_search(content):
            alist.append(n)
        for p in Picture.query.whoosh_search(content):
            alist.append(p)
        for a in Article.query.whoosh_search(content):
            alist.append(a)
        for i in Interaction.query.whoosh_search(content):
            alist.append(i)
        for t in Tag.query.whoosh_search(content):
            for _news in t.news:
                alist.append(News.query.get_or_404(_news.news_id))
            for _article in t.articles:
                alist.append(Article.query.get_or_404(_article.article_id))
            for _pic in t.pictures:
                alist.append(Picture.query.get_or_404(_pic.picture_id))
            for _interaction in t.interactions:
                alist.append(Interaction.query.get_or_404(_article.interaction_id))
        return Response(json.dumps([{
                "article_id":post.id,
                "img_url":post.img_url[0],
                "title":post.title,
                "author":User.query.get_or_404(post.author_id).name,
                "views":post.views,
                "tag":Tag.query.get_or_404(post.tag[0].tag_id).body if len([i for i in post.tag]) else "",
                "description":post.description,
                "time":post.time.strftime('%m/%d/%Y'),
                } for post in alist[:count-1]]
        ),mimetype='application/json')


@api.route('/hottag/',methods=['GET'])
def get_hottag():
    tags = rds.keys()
    hot_tags = sorted(tags, key=lambda w: int(rds.get(w)), reverse=True)[:10]
    return Response(json.dumps({
        "hot_tag":hot_tags
    }))
