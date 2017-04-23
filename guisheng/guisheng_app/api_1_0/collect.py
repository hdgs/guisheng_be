# coding: utf-8
from flask import render_template,jsonify,Response,g,request
from flask_login import current_user,login_required
import json
from ..models import Collect,News,Article,Interaction,Picture
from . import api
from .. import db

@api.route('/collect/', methods=['GET','POST'])
def collect():
    kind = int(request.get_json().get('kind'))
    a_id = int(request.get_json().get('article_id'))
    my_id = int(request.get_json().get('my_id'))
    collect = Collect()
    collect.author_id = my_id
    if kind == 1:
        if not Collect.query.filter_by(news_id=a_id).filter_by(author_id=my_id).first(): 
            if News.query.filter_by(id=a_id).first().published == 1:
                collect.news_id = a_id
                db.session.add(collect)
    if kind == 2:
        if not Collect.query.filter_by(picture_id=a_id).filter_by(author_id=my_id).first():
            if Picture.query.filter_by(id=a_id).first().published == 1:
                collect.picture_id = a_id
                db.session.add(collect)
    if kind == 3:
        if not Collect.query.filter_by(article_id=a_id).filter_by(author_id=my_id).first():
            if Article.query.filter_by(id=a_id).first().published == 1:
                collect.article_id = a_id
                db.session.add(collect)
    if kind == 4:
        if not Collect.query.filter_by(interaction_id=a_id).filter_by(author_id=my_id).first():
            if Interaction.query.filter_by(id=a_id).first().published == 1:
                collect.interaction_id = a_id
                db.session.add(collect)
    db.session.commit()
    return jsonify({
        'collected':collect.id
    })

@api.route('/collect_delete/', methods=['GET','POST'])
def collect_delete():
    kind = int(request.get_json().get('kind'))
    a_id = int(request.get_json().get('article_id'))
    my_id = int(request.get_json().get('my_id'))
    if kind == 1:
        collect = Collect.query.filter_by(news_id=a_id).filter_by(author_id=my_id).first()
    if kind == 2:
        collect = Collect.query.filter_by(picture_id=a_id).filter_by(author_id=my_id).first()
    if kind == 3:
        collect = Collect.query.filter_by(article_id=a_id).filter_by(author_id=my_id).first()
    if kind == 4:
        collect = Collect.query.filter_by(interaction_id=a_id).filter_by(author_id=my_id).first()
    db.session.delete(collect)
    db.session.commit()
    return jsonify({
        'deleted':collect.id
    })


