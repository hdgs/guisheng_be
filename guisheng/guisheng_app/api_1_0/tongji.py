# coding: utf-8
from flask import jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment,PostTag,Tag
from . import api
from operator import attrgetter
from guisheng_app import rds
from .. import db
from guisheng_app.decorators import admin_required,edit_required
from sqlalchemy import or_


def count_publisher_articles(publisher):
    news = News.query.filter_by(freshmen=0).filter_by(publisher=publisher.name).filter_by(published=1).count()
    articles = Article.query.filter_by(publisher=publisher.name).filter_by(published=1).count()
    interactions = Interaction.query.filter_by(publisher=publisher.name).filter_by(published=1).count()
    pictures = Picture.query.filter_by(freshmen=0).filter_by(publisher=publisher.name).filter_by(published=1).count()
    num = news + articles + interactions + pictures
    return num

def count_author_articles(author,month=0):
    num = 0
    if month == 0:
        news = News.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1).count()
        articles = Article.query.filter_by(author_id=author.id).filter_by(published=1).count()
        interactions = Interaction.query.filter_by(author_id=author.id).filter_by(published=1).count()
        pictures = Picture.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1).count()
        num = news + articles + interactions + pictures
        return num
    else:
        for n in News.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1):
            if n.time.month==month:
                num=num+1
        for a in Article.query.filter_by(author_id=author.id).filter_by(published=1):
            if a.time.month==month:
                num=num+1
        for i in Interaction.query.filter_by(author_id=author.id).filter_by(published=1):
            if i.time.month==month:
                num=num+1
        for p in Picture.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1):
            if p.time.month==month:
                num=num+1
        return num

def count_author_views(author,month=0):
    num = 0
    n_views = 0
    a_views = 0
    i_views = 0
    p_views = 0
    if month==0:
        for n in News.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1):
            n_views = n_views + n.views
        for a in Article.query.filter_by(author_id=author.id).filter_by(published=1):
            a_views = a_views + a.views
        for i in Interaction.query.filter_by(author_id=author.id).filter_by(published=1):
            i_views = i_views + i.views
        for p in Picture.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1):
            p_views = p_views + p.views
        all_views = n_views + a_views + i_views + p_views
        return all_views
    else:
        for n in News.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1):
            if n.time.month==month:
                n_views = n_views + n.views
        for a in Article.query.filter_by(author_id=author.id).filter_by(published=1):
            if a.time.month==month:
                a_views = a_views + a.views
        for i in Interaction.query.filter_by(author_id=author.id).filter_by(published=1):
            if i.time.month==month:
                i_views = i_views + i.views
        for p in Picture.query.filter_by(freshmen=0).filter_by(author_id=author.id).filter_by(published=1):
            if p.time.month==month:
                p_views = p_views + p.views
        all_views = n_views + a_views + i_views + p_views
        return all_views


@api.route('/rank/articles/', methods=['GET'])
@edit_required
def rank_articles():
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    tolist=[]
    for n in News.query.filter_by(published=1).filter_by(freshmen=0).order_by(News.views.desc()).limit(count+page*count):
        tolist.append(n)
    for p in Picture.query.filter_by(published=1).filter_by(freshmen=0).order_by(Picture.views.desc()).limit(count+page*count):
        tolist.append(p)
    for a in Article.query.filter_by(published=1).order_by(Article.views.desc()).limit(count+page*count):
        tolist.append(a)
    for i in Interaction.query.filter_by(published=1).order_by(Interaction.views.desc()).limit(count+page*count):
        tolist.append(i)
    tolist.sort(key=attrgetter('views'),reverse=True)
    if len(tolist)<page*count:
        alist = tolist[(page-1)*count:]
    else:
        alist = tolist[(page-1)*count:(page)*count]
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
                } for content in alist]
        ),mimetype='application/json')


@api.route('/rank/authors/', methods=['GET'])
@edit_required
def rank_authors():
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    authors = User.query.filter_by(role_id=3).filter_by(user_role=1).all()
    adict = {}
    bdict = {}
    for u in authors:
        adict[u.name] = count_author_views(u)
        bdict[u.name] = count_author_articles(u)
    sort_dict = sorted(adict.items(),key=lambda item:item[1],reverse=True)
    if len(authors)<page*count:
        alist = sort_dict[(page-1)*count:]
    else:
        alist = sort_dict[(page-1)*count:(page)*count]
    return Response(json.dumps([{
        "name":a[0],
        "articles_sum":bdict[a[0]],
        "views_sum":adict[a[0]],
        } for a in alist]
    ),mimetype='application/json')


@api.route('/rank/publishers/', methods=['GET'])
@edit_required
def rank_publishers():
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    publishers = [p.name for p in User.query.filter(or_(User.role_id==2,User.role_id==4)).all()]
    adict={}
    for p in User.query.filter(or_(User.role_id==2,User.role_id==4)).all():
        adict[p.name] = count_publisher_articles(p)
    sort_dict = sorted(adict.items(),key=lambda item:item[1],reverse=True)
    if len(publishers)<page*count:
        alist = sort_dict[(page-1)*count:]
    else:
        alist = sort_dict[(page-1)*count:(page)*count]
    return Response(json.dumps([{
        "name":a[0],
        "articles_sum":a[1],
        } for a in alist]
    ),mimetype='application/json')


@api.route('/rank/articles/<int:month>/', methods=['GET'])
@edit_required
def rank_month_articles(month):
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    tolist=[]
    for n in News.query.filter_by(published=1).filter_by(freshmen=0).order_by(News.views.desc()).limit(count+page*count):
        if n.time.month==month:
            tolist.append(n)
    for p in Picture.query.filter_by(published=1).filter_by(freshmen=0).order_by(Picture.views.desc()).limit(count+page*count):
        if p.time.month==month:
            tolist.append(p)
    for a in Article.query.filter_by(published=1).order_by(Article.views.desc()).limit(count+page*count):
        if a.time.month==month:
            tolist.append(a)
    for i in Interaction.query.filter_by(published=1).order_by(Interaction.views.desc()).limit(count+page*count):
        if i.time.month==month:
            tolist.append(i)
    tolist.sort(key=attrgetter('views'),reverse=True)
    if len(tolist)<page*count:
        alist = tolist[(page-1)*count:]
    else:
        alist = tolist[(page-1)*count:(page)*count]
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
                } for content in alist]
        ),mimetype='application/json')


@api.route('/rank/authors/<int:month>/', methods=['GET'])
@edit_required
def rank_month_authors(month):
    page = int(request.args.get('page'))
    count = int(request.args.get('count'))
    authors = User.query.filter_by(role_id=3).filter_by(user_role=1).all()
    adict = {}
    bdict = {}
    for u in authors:
        adict[u.name] = count_author_views(u,month)
        bdict[u.name] = count_author_articles(u,month)
    sort_dict = sorted(adict.items(),key=lambda item:item[1],reverse=True)
    if len(authors)<page*count:
        alist = sort_dict[(page-1)*count:]
    else:
        alist = sort_dict[(page-1)*count:(page)*count]
    return Response(json.dumps([{
        "name":a[0],
        "articles_sum":bdict[a[0]],
        "views_sum":adict[a[0]],
        } for a in alist]
    ),mimetype='application/json')


