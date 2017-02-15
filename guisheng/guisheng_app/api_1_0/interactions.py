# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user
import json
from ..models import Role,User,Interaction,Tag,PostTag
from . import api
from .. import db

@api.route('/interaction/<int:id>/',methods=['GET'])
def get_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    like_degree_one = interaction.light.filter_by(like_degree=0).count()
    like_degree_two = interaction.light.filter_by(like_degree=1).count()
    like_degree_three = interaction.light.filter_by(like_degree=2).count()
    user_role = -1 if current_user.is_anonymous else 0
    interaction.views+=1
    db.session.commit()
    return Response(json.dumps({
        "kind":4,
        "title":interaction.title,
        "author":User.query.get_or_404(interaction.author_id).name,
        "time":interaction.time.strftime('%Y-%m-%d'),
        "body":interaction.body,
        "like":[like_degree_one,like_degree_two,like_degree_three],
        "editor":interaction.editor,
        "user_role":user_role,
        "author_id":interaction.author_id
        }),mimetype='application/json')


@api.route('/interactions/recommend/',methods=['GET','POST'])
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
            "title":Interaction.query.filter_by(id=interaction_id).first().title,
            "description":Interaction.query.filter_by(id=interaction_id).first().description,
            "author":User.query.get_or_404(Interaction.query.filter_by(id=interaction_id).first().author_id).name,
            "tag":tag.body,
            "views":Interaction.query.filter_by(id=interaction_id).first().views
        }for interaction_id in recommend_interactions]
    ),mimetype='application/json')


