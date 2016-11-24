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
        "time":interaction.time.strftime('%Y-%m-%d %H:%M:%S %f'),
        "body":interaction.body,
        }),mimetype='application/json')

