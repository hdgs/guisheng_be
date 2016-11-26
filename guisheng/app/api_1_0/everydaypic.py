# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api

@api.route('/everydaypic/', methods=['GET','POST'])
def get_everydaypic():
    everydaypic = Everydaypic.query.first()
    return Response(json.dumps({
        "img_url":everydaypic.img_url,
        "climate_url":everypic.climate_url,
        "climate":everydaypic.climate,
        "date":everydaypic.date,
        }),mimetype='application/json')


 
