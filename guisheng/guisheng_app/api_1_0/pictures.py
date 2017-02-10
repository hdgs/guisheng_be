# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,Picture,Tag,PostTag
from . import api
from .. import db
from guisheng_app.decorators import admin_required

def add_tags(pics, tags, update):
    """
    判断
        向数据库中添加tag实例
        向数据库中添加tag和pics关系
    """
    # add tag
    for tag in tags:
        tag_in_db = Tag.query.filter_by(body=tag).first()
        if tag_in_db:
            if (not update):
                tag_in_db.count += 1
                db.session.add(tag_in_db)
        else:
            add_tag = Tag(body=tag, count=1)
            db.session.add(add_tag)
        db.session.commit()
    # add course & tag
    for tag in tags:
        get_tag = Tag.query.filter_by(body=tag).first()
        post_tags = [t.tag_id for t in pics.tag.all()]
        if get_tag.id in post_tags:
            if (not update):
                post_tag = PostTag.query.filter_by(
                    tag_id=get_tag.id, picture_id=pics.id,
                ).first()
                post_tag.count += 1
                db.session.add(post_tag)
        else:
            post_tag = PostTag(
                tag_id=get_tag.id, picture_id=pics.id, count=1
            )
            db.session.add(post_tag)
        db.session.commit()

def update_tags(pics):
    """
        向数据库中更新tag实例
        向数据库中更新tag和pics关系
    """
    tags = request.json.get("tags").split()
    tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
    post_tag_ids = [t.tag_id for t in pics.tag.all()]
    # update tag && postTag
    for post_tag_id in post_tag_ids:
        if  post_tag_id not in tags_id:
            tag = Tag.query.filter_by(id=post_tag_id).first()
            tag.count -= 1
            db.session.add(tag)
            post_tag = PostTag.query.filter_by(
                tag_id=post_tag_id, picture_id=pics.id,
            ).first()
            db.session.delete(post_tag)
            db.session.commit()

@api.route('/pics/<int:id>/', methods=['GET'])
def get_pic(id):
    pic = Picture.query.get_or_404(id)
    user_role = -1 if g.current_user.is_anonymous else 0
    pic.views+=1
    db.session.commit()
    return Response(json.dumps({
        "kind":2,
        "title":pic.title,
        "author":User.query.get_or_404(pic.author_id).name,
        "time":pic.time.strftime('%Y/%m/%d %H:%M'),
        "pics":pic.img_url,
        "introduction":pic.introduction,
        "likes":pic.like.count(),
        "views":pic.views,
        "commentCount":pic.comments.filter_by(comment_id=-1).count(),
        "editor":pic.editor,
        "user_role":user_role
    }),mimetype='application/json')

@api.route('/pics/recommend/', methods=['GET','POST'])
def recommend_pics():
    pic_id = int(request.get_json().get('article_id'))
    now_pic = Picture.query.get_or_404(pic_id)
    try:
        tag_id = now_pic.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        pics = []
        for _pic in tag.pictures:
            pics.append(_pic.picture_id)
        sortlist = sorted(pics,key=lambda id: Picture.query.get_or_404(id).views,reverse=True) 
        recommend_pics = sortlist[:3] if len(sortlist)>=4 else sortlist
    except:
       recommend_pics = []
    return Response(json.dumps([{
            "img_url":Picture.query.get_or_404(pic_id).img_url,
            "title":Picture.query.get_or_404(pic_id).title,
            "author":User.query.get_or_404(Picture.query.get_or_404(pic_id).author_id).name,
            "views":Picture.query.get_or_404(pic_id).views,
            "tag":tag.body,
        } for pic_id in recommend_pics]
    ),mimetype='application/json')

@api.route('/pics/', methods=['GET','POST'])
@admin_required
def add_pics():
    if request.method == "POST":
        pics = Picture.from_json(request.get_json())
        db.session.add(pics)
        db.session.commit()
        add_tags(pics, request.json.get("tags").split(), False)
        return jsonify({
            'id': pics.id
        }), 201

@api.route('/pics/<int:id>/', methods=["GET", "PUT"])
@admin_required
def update_pics(id):
    pics = Picture.query.get_or_404(id)
    json = request.get_json()
    if request.method == "PUT":
        pics.title = json.get('title')
        pics.img_url = json.get('img_url')
        pics.author = json.get('author')
        pics.introduction = json.get('introduction')
        pics.author =  User.query.get_or_404(json.get('author_id'))
        db.session.add(pics)
        db.session.commit()
        add_tags(pics, request.json.get("tags").split(), True)
        update_tags(pics)
        return jsonify({
            'update': pics.id
        }), 200

@api.route('/pics/<int:id>/', methods=["GET", "DELETE"])
@admin_required
def delete_pics(id):
    pics = Picture.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(pics)
        db.session.commit()
        return jsonify({
            'deleted': pics.id
        }), 200

