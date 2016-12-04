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
    i_id = request.get_json().get('article_id',type=int)
    interact_tag = PostTag.query.filter_by(interaction_id=i_id).first()
    pagination = interact_tag.interactions.order_by(Interaction.views.desc()).paginate(
            0,per_page=3,error_out=False)
    command_interactions = pagination.items
    return Response(json.dumps([{
            "title":interaction.title,
            "description":interaction.description,
            "author":User.query.get_or_404(interaction.author_id).name,
            "tag":interact_tag,
            "views":interaction.views
        }for interaction in command_interactions]
    ),mimetype='application/json')


