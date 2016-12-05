# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api


@api.route('/interaction/<int:id>/',methods=['GET'])
def get_interaction(id):
    interaction = Interaction.query.get_or_404(id)
    return Response(json.dumps({
        "title":interaction.title,
        "author":User.query.get_or_404(interaction.author_id).name,
        "time":interaction.time.strftime('%m/%d/%Y'),
        "body":interaction.body,
        }),mimetype='application/json')
    

@api.route('/interactions/',methods=['GET','POST'])
def command_interactions():
    interact_id = int(request.get_json().get('article_id'))
    now_interact = Interaction.query.get_or_404(interact_id)
    tag_id = now_interact.tag[0].tag_id
    tag = Tag.query.get_or_404(tag_id)
    interactions = []
    for _interaction in tag.interactions:
        interactions.append(_interaction.interaction_id)
    sortlist = sorted(interactions, key=lambda id: Interaction.query.get_or_404(id).views,reverse=True)
    command_interactions = sortlist[:3]
    return Response(json.dumps([{
            "title":interaction.title,
            "description":interaction.description,
            "author":User.query.get_or_404(interaction.author_id).name,
            "tag":tag.body,
            "views":interaction.views
        }for interaction in command_interactions]
    ),mimetype='application/json')

