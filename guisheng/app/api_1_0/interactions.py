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
    interaction_id = request.get_json().get('article_id')
    interaction_tag = Interaction.query.get_or_404(interaction_id).tag[0]
    all_interactions = Interaction.query.order_by(Interaction.views.desc()).all()
    command_interactions = []
    for i in all_interactions:
        if i.tag[0]==interaction_tag:
            command_interactions.append(i)
    return Response(json.dumps([{
            "title":interaction.title,
            "description":interaction.description,
            "author":User.query.get_or_404(interaction.author_id).name,
            "tag":interaction.tag[0],
            "views":interaction.views
        }for interaction in command_interactions]
    ),mimetype='application/json')


