# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,Picture,Tag,PostTag
from . import api
from .. import db
from guisheng_app.decorators import admin_required

@api.route('/pics/<int:id>/', methods=['GET'])
def get_pic(id):
    pic = Picture.query.get_or_404(id)
    user_role = -1 if current_user.is_anonymous else 0
    pic.views+=1
    db.session.commit()
    return Response(json.dumps({
        "id":pic.id,
        "kind":2,
        "title":pic.title,
        "author":User.query.get_or_404(pic.author_id).name,
        "time":pic.time.strftime('%Y-%m-%d'),
        "pics":pic.img_url,
        "introduction":pic.introduction,
        "likes":pic.like.count(),
        "views":pic.views,
        "commentCount":pic.comments.filter_by(comment_id=-1).count(),
        "editor":pic.editor,
        "user_role":user_role,
        "author_id":pic.author_id
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
            "kind":Picture.query.get_or_404(pic_id).kind,
            "article_id":Picture.query.get_or_404(pic_id).id
        } for pic_id in recommend_pics]
    ),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
@api.route('/pics/',methods=['GET','POST'])
#@admin_required
def add_pics():
    if request.method == 'POST':
        pics = Picture.from_json(request.get_json())
        db.session.add(pics)
        db.session.commit()
        tags = request.get_json().get('tags').split()
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
            'id':pics.id
        }), 201

@api.route('/pics/<int:id>/',methods=['GET','PUT'])
#@admin_required
def update_pics(id):
    pics = Picture.query.get_or_404(id)
    if request.method == 'PUT':
        pics.title = request.get_json().get('title')
        pics.img_url = request.get_json().get('img_url')
        pics.introduction = request.get_json().get('introduction')
        pics.author =  User.query.get_or_404(request.get_json().get('author_id'))
        db.session.add(pics)
        db.session.commit()

        tags = request.get_json().get('tags').split()
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            pics_tags = [t.tag_id for t in pics.tag.all()]
            if get_tag.id not in pics_tags:
                post_tag = PostTag(pics_tags=get_tag,pictures=pics)
                db.session.add(post_tag)
                db.session.commit()

        tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
        pics_tag_ids = [t.tag_id for t in pics.tag.all()]
        for pics_tag_id in pics_tag_ids:
            if  pics_tag_id not in tags_id:
                p_tag = Tag.query.get_or_404(pics_tag_id)
                post_tag = PostTag.query.filter_by(picture_tags=p_tag,pictures=pics)
                db.session.delete(post_tag)
                db.session.commit()
        return jsonify({
            'update': pics.id
        }),200

@api.route('/pics/<int:id>/', methods=["GET", "DELETE"])
#@admin_required
def delete_pics(id):
    pics = Picture.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(pics)
        db.session.commit()
        return jsonify({
            'deleted': pics.id
        }), 200

