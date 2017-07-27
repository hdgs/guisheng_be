# coding: utf-8

import json

from flask import request,jsonify,Response
from flask_login import login_user, logout_user, current_user, login_required

from . import api
from guisheng_app import db
from guisheng_app.decorators import admin_required
from guisheng_app.models import Special,ChildTopic,Role,User,News,Picture,Tag,PostTag,Image,Collect
from operator import attrgetter

COUNT = 10

@api.route('/special/feed/',methods=['POST'])
def special_main_page():
    if request.method == 'POST':
        special_id = request.get_json().get('id')
        tolist = []
        
        for n in News.query.filter_by(special_id=special_id).order_by(News.time.desc()):
            tolist.append(n) 
        for p in Picture.query.filter_by(special_id=special_id).order_by(Picture.time.desc()):
            tolist.append(p)
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
                "description":content.description,
                "child_topic_id":content.childtopic_id
                } for content in tolist]
        ),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
#ToDo
#Test And Debug

@api.route('/special/',methods = ['POST'])
@admin_required
def add_special():
    if request.method == 'POST':
        
        name = request.get_json().get('special_name')
        description = request.get_json().get('description')
        special = Special()
        special.special_name = name
        special.description = description

        db.session.add(special)
        db.session.commit()
        
        return jsonify({
            'id':special.id
        }),201

@api.route('/special/<int:id>/',methods = ['POST'])
@admin_required
def add_childtopic(id):
    if request.method == 'POST':
        name = request.get_json().get('childtopic_name')
        
        childtopic = ChildTopic()
        childtopic.childtopic_name = name
        childtopic.special_id = id

        db.session.add(childtopic)
        db.session.commit()

        return jsonify({
            'id':childtopic.id
        }),201

@api.route('/special/<int:special_id>/<int:childtopic_id>/article/',methods=['POST'])
@admin_required
def add_special_article(special_id,childtopic_id):
    if request.method =='POST':
         
         article = News.from_json(request.get_json())
         article.special_id = special_id
         article.childtopic_id = childtopic_id
         article.freshmen=1

         db.session.add(article)
         db.session.commit()

         tags = request.get_json().get('tags')
         for tag in tags:
             if not Tag.query.filter_by(body=tag).first():
                 t = Tag(body=tag)
                 db.session.add(t)
                 db.session.commit()
             get_tag = Tag.query.filter_by(body=tag).first()
             news_tags = [t.tag_id for t in article.tag.all()]
             if get_tag.id not in news_tags:
                 post_tag = PostTag(news_tags=get_tag,news=article)
                 db.session.add(post_tag)
                 db.session.commit()
         return jsonify({
             'id': article.id
         }), 201


@api.route('/special/<int:special_id>/<int:childtopic_id>/picture/',methods=['POST'])
@admin_required
def add_special_picture(special_id,childtopic_id):
    if request.method == 'POST':
        title = request.get_json().get('title')
        author = request.get_json().get('author')
        if User.query.filter_by(name=author).first():
            if Picture.query.filter_by(title=title).first():
                pics = Picture.query.filter_by(title=title).first()
            else:
                
                pics = Picture.from_json(request.get_json())
                pics.special_id = special_id
                pics.childtopic_id = childtopic_id
                pics.freshmen=1
                db.session.add(pics)
                db.session.commit()

            img_url = request.get_json().get('img_url')
            introduction = request.get_json().get('description')
            image = Image(img_url=img_url,introduction=introduction,picture=pics)
            db.session.add(image)
            db.session.commit()
            tags = request.get_json().get('tags')
            for tag in tags:
                if not Tag.query.filter_by(body=tag).first():
                    t = Tag(body=tag)
                    db.session.add(t)
                    db.session.commit()
                get_tag = Tag.query.filter_by(body=tag).first()
                pics_tags = [t.tag_id for t in pics.tag.all()]
                if get_tag.id not in pics_tags:
                    post_tag = PostTag(picture_tags=get_tag,pictures=pics)
                    db.session.add(post_tag)
                    db.session.commit()
            return jsonify({
                'id':pics.id,
            }), 201


@api.route('/special/list/',methods = ['GET'])
@admin_required
def special_list():
    page = int(request.args.get('page'))
    specials = []
    specials = Special.query.order_by(Special.id).limit(COUNT).offset((page-1)*COUNT)
    
    return Response(
            json.dumps
            (
                [
                    {
                        "id":special.id
                    }
                    for special in specials
                ],
            ),
        mimetype ='application/json')


@api.route('/special/list/<int:special_id>/',methods=['GET'])
@admin_required
def childtopic_list(special_id):
    page = int(request.args.get('page'))
    childtopics = ChildTopic.query.filter_by(special_id = special_id).order_by(ChildTopic.id).limit(COUNT).offset((page-1)*COUNT)
    return Response(
            json.dumps
            (
                [
                    {
                        "id":childtopic.id 
                    }
                    for childtopic in childtopics
                ],
            ),
        mimetype ='application/json')


@api.route('/special/list/<int:special_id>/<int:childtopic_id>/',methods=['GET'])
@admin_required
def all_posts(special_id,childtopic_id):
    page = int(request.args.get('page'))-1
    tolist = []

    for n in News.query.filter_by(special_id=special_id).filter_by(childtopic_id=childtopic_id).order_by(News.time.desc()).limit(COUNT+page*COUNT):
            tolist.append(n) 
    for p in Picture.query.filter_by(special_id=special_id).filter_by(childtopic_id=childtopic_id).order_by(Picture.time.desc()).limit(COUNT+page*COUNT):
            tolist.append(p) 
    
    tolist.sort(key=attrgetter('time'),reverse=True)
    alist = tolist[page*COUNT:(page+1)*COUNT]

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
                "description":content.description,
                "published":content.published
                } for content in alist]
    ),mimetype='application/json')
