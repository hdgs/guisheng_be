# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,Interaction,Tag,PostTag,Collect
from . import api
from .. import db
from guisheng_app.decorators import admin_required

@api.route('/interaction/<int:id>/',methods=['GET','POST'])
def get_interaction(id):
    if request.method == "POST":
        my_id = int(request.get_json().get('my_id'))
        interaction = Interaction.query.get_or_404(id)
        like_degree_one = interaction.light.filter_by(like_degree=0).count()
        like_degree_two = interaction.light.filter_by(like_degree=1).count()
        like_degree_three = interaction.light.filter_by(like_degree=2).count()
        interaction.views+=1
        db.session.commit()
        if my_id == -1:
            collected=0
        else:
            if Collect.query.filter_by(interaction_id=id).filter_by(author_id=my_id).first():
                collected=1
            else:
                collected=0
        return Response(json.dumps({
            "kind":4,
            "img_url":User.query.get_or_404(interaction.author_id).img_url,
            "title":interaction.title,
            "author":User.query.get_or_404(interaction.author_id).name,
            "time":interaction.time.strftime('%Y-%m-%d'),
            "body":interaction.body,
            "like_degree":[like_degree_one,like_degree_two,like_degree_three],
            "editor":interaction.editor,
            "author_id":interaction.author_id,
            "commentCount":interaction.comments.count(),
            "collected":collected,
            "music":{
                    "title":"",
                    "music_img_url":"",
                    "music_url":"",
                    "singer":""
            },
            "film":{
                   "film_url":"",
                   "scores":"",
                   "film_img_url":""
            }
            }),mimetype='application/json')


@api.route('/interaction/recommend/',methods=['GET','POST'])
def recommend_interactions():
    interact_id = int(request.get_json().get('article_id'))
    now_interact = Interaction.query.get_or_404(interact_id)
    try:
        tag_id = now_interact.tag[0].tag_id
        tag = Tag.query.get_or_404(tag_id)
        interactions = []
        for _interaction in tag.interactions:
            interactions.append(_interaction.interaction_id)
        sortlist = sorted(interactions, key=lambda id: Interaction.query.get_or_404(id).views,reverse=True)
        recommend_interactions = sortlist[:3] if len(sortlist)>=4 else sortlist
    except:
        recommend_interactions = []
    return Response(json.dumps([{
            "title":Interaction.query.get_or_404(interaction_id).title,
            "description":Interaction.query.get_or_404(interaction_id).description,
            "author":User.query.get_or_404(Interaction.query.get_or_404(interaction_id).author_id).name,
            "tag":tag.body,
            "views":Interaction.query.get_or_404(interaction_id).views,
            "kind":Interaction.query.get_or_404(interaction_id).kind,
            "article_id":Interaction.query.get_or_404(interaction_id).id
        }for interaction_id in recommend_interactions]
    ),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
@api.route('/interaction/',methods=['GET','POST'])
@admin_required
def add_interaction():
    if request.method == 'POST':
        interaction = Interaction.from_json(request.get_json())
        db.session.add(interaction)
        db.session.commit()
        tags = request.get_json().get('tags')
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            interaction_tags = [t.tag_id for t in interaction.tag.all()]
            if get_tag.id not in interaction_tags:
                post_tag = PostTag(tag_id=get_tag.id,interaction_id=interaction.id)
                db.session.add(post_tag)
                db.session.commit()
        return jsonify({
            'id':interaction.id
        }), 201

@api.route('/interaction/<int:id>/',methods=['GET','PUT'])
@admin_required
def update_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    if request.method == 'PUT':
        interaction.title = request.get_json().get('title')
        interaction.img_url = request.get_json().get('img_url')
        interaction.author = User.query.filter_by(name=request.get_json().get('name')).first()
        interaction.description = request.get_json().get('description')
        db.session.add(interaction)
        db.session.commit()

        tags = request.get_json().get('tags')
        for tag in tags:
            if not Tag.query.filter_by(body=tag).first():
                t = Tag(body=tag)
                db.session.add(t)
                db.session.commit()
            get_tag = Tag.query.filter_by(body=tag).first()
            interaction_tags = [t.tag_id for t in interaction.tag.all()]
            if get_tag.id not in interaction_tags:
                post_tag = PostTag(interaction_tags=get_tag,interactions=interaction)
                db.session.add(post_tag)
                db.session.commit()

        tags_id = [Tag.query.filter_by(body=tag).first().id for tag in tags]
        interaction_tag_ids = [t.tag_id for t in interaction.tag.all()]
        for interaction_tag_id in interaction_tag_ids:
            if  interaction_tag_id not in tags_id:
                i_tag = Tag.query.get_or_404(interaction_tag_id)
                post_tag = PostTag.query.filter_by(interaction_tags=i_tag,interactions=interaction).first()
                db.session.delete(post_tag)
                db.session.commit()
        return jsonify({
            'update': interaction.id
        }),200

@api.route('/interaction/<int:id>/body/', methods=["GET", "PUT"])
@admin_required
def update_interaction_body(id):
    interaction = Interaction.query.get_or_404(id)
    if request.method == "PUT":
        interaction.body = request.get_json().get('body')
        db.session.add(interaction)
        db.session.commit()
        return jsonify({
            'update': interaction.id
        }), 200

@api.route('/interaction/<int:id>/', methods=["GET", "DELETE"])
@admin_required
def delete_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(interaction)
        db.session.commit()
        return jsonify({
            'deleted': interaction.id
        }), 200
