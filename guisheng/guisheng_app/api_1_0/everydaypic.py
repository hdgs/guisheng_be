# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Everydaypic
from . import api

@api.route('/everydaypic/', methods=['GET','POST'])
def get_everydaypic():
    everydaypic = Everydaypic.query.first()
    return Response(json.dumps({
        "img_url":everydaypic.img_url,
        "climate_url":everydaypic.climate_url,
        "climate":everydaypic.climate,
        "date":everydaypic.date,
        }),mimetype='application/json')


 
