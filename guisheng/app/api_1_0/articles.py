# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,Article
from . import api


@api.route('/article/<int:id>/', methods=['GET','POST'])
def get_article(id):
    article = Article.query.get_or_404(id)
    return Response(json.dumps({
        "title":article.title,
        "img_url":article.img_url,
        "author":User.query.get_or_404(article.author_id).name,
        "time":article.time.strftime('%m/%d/%Y'),
        "body":article.body,
        "music":{
            "title":article.music_title,
            "music_url":article.music_url,
            },
        "film":{
            "film_url":article.film_url,
            }
        }),mimetype='application/json')


