# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,Picture,Tag,PostTag,Image,Collect
from . import api
from .. import db
from guisheng_app.decorators import admin_required

@api.route('/pics/<int:id>/', methods=['POST'])
def get_pic(id):
    if request.method == "POST":
        my_id = int(request.get_json().get('my_id'))
        pic = Picture.query.get_or_404(id)
        if pic.published == 1:
            pics = [p.img_url for p in pic.img_url]
            introductions = [p.introduction for p in pic.img_url]
            pic.views+=1
            db.session.commit()
            if my_id == -1:
                collected=0
            else:
                if Collect.query.filter_by(picture_id=id).filter_by(author_id=my_id).first():
                    collected=1
                else:
                    collected=0
            return Response(json.dumps({
                "id":pic.id,
                "kind":2,
                "title":pic.title,
                "author":User.query.get_or_404(pic.author_id).name,
                "img_url":User.query.get_or_404(pic.author_id).img_url,
                "time":pic.time.strftime('%Y-%m-%d'),
                "pics":pics,
                "introduction":introductions,
                "likes":pic.like.count(),
                "views":pic.views,
                "commentCount":pic.comments.count(),
                "editor":pic.editor,
                "author_id":pic.author_id,
                "collected":collected
            }),mimetype='application/json')

@api.route('/pics/recommend/', methods=['GET','POST'])
def recommend_pics():
    pic_id = int(request.get_json().get('article_id'))
    now_pic = Picture.query.get_or_404(pic_id)
    recommend_pics = []
    sortlist = []
    pics = []
    if now_pic.tag:
        tag_id = now_pic.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        for _pic in tag.pictures:
            if Picture.query.filter_by(id=_pic.picture_id).first():
                if Picture.query.get_or_404(_pic.picture_id).published == 1 \
                   and _pic.picture_id != pic_id:
                    pics.append(_pic.picture_id)
        sortlist = sorted(pics,key=lambda id: Picture.query.get_or_404(id).views,reverse=True) 
        recommend_pics = sortlist[:3] if len(sortlist)>=4 else sortlist
    return Response(json.dumps([{
            "img_url":[p.img_url for p in Picture.query.get_or_404(pic_id).img_url][0],
            "title":Picture.query.get_or_404(pic_id).title,
            "author":User.query.get_or_404(Picture.query.get_or_404(pic_id).author_id).name,
            "views":Picture.query.get_or_404(pic_id).views,
            "tag":tag.body,
            "kind":Picture.query.get_or_404(pic_id).kind,
            "article_id":Picture.query.get_or_404(pic_id).id
        } for pic_id in recommend_pics]
    ),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
@api.route('/pics/<int:id>/', methods=['GET'])
@admin_required
def show_pic(id):
    pic = Picture.query.get_or_404(id)
    pics = [p.img_url for p in pic.img_url]
    introductions = [p.introduction for p in pic.img_url]
    tagids=[pt.tag_id for pt in PostTag.query.filter_by(picture_id=id).all()]
    tags=[Tag.query.filter_by(id=t).first().body for t in tagids]
    return Response(json.dumps({
        "id":pic.id,
        "kind":2,
        "title":pic.title,
        "author":User.query.get_or_404(pic.author_id).name,
        "img_url":User.query.get_or_404(pic.author_id).img_url,
        "time":pic.time.strftime('%Y-%m-%d'),
        "pics":pics,
        "introduction":introductions,
        "likes":pic.like.count(),
        "views":pic.views,
        "commentCount":pic.comments.count(),
        "editor":pic.editor,
        "author_id":pic.author_id,
        "tags":tags
    }),mimetype='application/json')

@api.route('/pics/',methods=['POST'])
@admin_required
def add_pics():
    if request.method == 'POST':
        title = request.get_json().get('title')
        author = request.get_json().get('author')
        if User.query.filter_by(name=author).first():
            if Picture.query.filter_by(title=title).first():
                pics = Picture.query.filter_by(title=title).first()
            else:
                pics = Picture.from_json(request.get_json())
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

@api.route('/pics/<int:id>/',methods=['PUT'])
@admin_required
def update_pics(id):
    pics = Picture.query.get_or_404(id)
    if request.method == 'PUT':
        pics.title = request.get_json().get('title')
        pics.author = User.query.filter_by(name=request.get_json().get('author')).first()
        db.session.add(pics)
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

        tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
        pics_tag_ids = [t.tag_id for t in pics.tag.all()]
        for pics_tag_id in pics_tag_ids:
            if  pics_tag_id not in tags_id:
                p_tag = Tag.query.get_or_404(pics_tag_id)
                post_tag = PostTag.query.filter_by(picture_tags=p_tag,pictures=pics).first()
                db.session.delete(post_tag)
                db.session.commit()
        return jsonify({
            'update': pics.id
        }),200

@api.route('/pics/<int:id>/', methods=['DELETE'])
@admin_required
def delete_pics(id):
    pics = Picture.query.get_or_404(id)
    db.session.delete(pics)
    db.session.commit()
    return jsonify({
        'deleted': pics.id
    }), 200

@api.route('/pics/<int:id>/pic/<int:index>/', methods=['DELETE'])
@admin_required
def delete_one_pic(id,index):
    pics = Picture.query.get_or_404(id)
    imgs = [i.id for i in pics.img_url]
    image = Image.query.get_or_404(imgs[index])
    db.session.delete(image)
    db.session.commit()
    return jsonify({
        'deleted': pics.id,
        'index':index
    }),200
