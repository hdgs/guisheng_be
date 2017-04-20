# coding: utf-8
from flask import render_template,jsonify,Response,g,request
import json
from ..models import Role,User,News,Picture,Article,Interaction,Everydaypic,\
        Collect,Like,Light,Comment
from . import api
from datetime import datetime,timedelta
from guisheng_app import db

def get_time(comment_time):
    now_time = datetime.utcnow()
    today = datetime.date(now_time)
    comment_date = datetime.date(comment_time)
    if now_time.strftime('%Y') == comment_time.strftime('%Y'):
        if comment_date==today:
            time = comment_time.strftime('%H:%M')
        elif comment_date==today+timedelta(days=-1):
            time = " ".join([u"昨天",comment_time.strftime('%H:%M')])
        else:
            time = comment_time.strftime('%m-%d')
    else:
        time = comment_time.strftime('%Y-%m-%d')


@api.route('/comments/',methods=['GET'])
def get_comments():
    kind = int(request.args.get("kind"))
    a_id = int(request.args.get("article_id"))
    if kind == 1:
        comments = Comment.query.filter_by(news_id=a_id).order_by(Comment.time.asc()).all()
        responses = Comment.query.filter_by(news_id=a_id).order_by(Comment.time.asc()).all()
    elif kind == 2:
        comments = Comment.query.filter_by(picture_id=a_id).order_by(Comment.time.asc()).all()
        responses = Comment.query.filter_by(picture_id=a_id).order_by(Comment.time.asc()).all()
    elif kind == 3:
        comments = Comment.query.filter_by(article_id=a_id).order_by(Comment.time.asc()).all()
        responses = Comment.query.filter_by(article_id=a_id).order_by(Comment.time.asc()).all()
    else:
        comments = Comment.query.filter_by(interaction_id=a_id).order_by(Comment.time.asc()).all()
        responses = Comment.query.filter_by(interaction_id=a_id).order_by(Comment.time.asc()).all()
    return Response(json.dumps([{
            "name":(User.query.get_or_404(comment.author_id)).name,
            "article_id":a_id,
            "comment_id":comment.id,
            "img_url":(User.query.get_or_404(comment.author_id)).img_url,
            "message":comment.body,
            "user_role":(User.query.get_or_404(comment.author_id)).user_role,
            "comments":[{
                "name":(User.query.get_or_404(comment.author_id)).name,
                "article_id":a_id,
                "comment_id":response.id,
                "img_url":(User.query.get_or_404(response.author_id)).img_url,
                "message":response.body,
                "user_role":(User.query.get_or_404(comment.author_id)).user_role,
                "likes":response.like.count(),
                }for response in responses],
            "likes":comment.like.count(),
            "time":get_time(comment.time),
            "user_id":comment.author_id
        } for comment in comments]
    ),mimetype='application/json')


@api.route('/comments/',methods=['GET','POST'])
def create_comments():
    if request.method == 'POST':
        comment = Comment()
        kind = int(request.get_json().get("kind"))

        if kind == 1:
            comment.news_id = request.get_json().get("article_id")
        if kind == 2:
            comment.picture_id = request.get_json().get("article_id")
        if kind == 3:
            comment.article_id = request.get_json().get("article_id")
        if kind == 4:
            comment.interaction_id = request.get_json().get("article_id")

        comment.comment_id = request.get_json().get("comment_id")
        comment.body = request.get_json().get("message")
        comment.author_id = request.get_json().get("user_id")
        db.session.add(comment)
        db.session.commit()
        return Response(json.dumps({
            "status":"200",
            }),mimetype='application/json')

@api.route('/comments/<int:id>/like/')
def get_comment_likes(id):
    comment = Comment.query.get_or_404(id)
    likes = comment.like.count()
    return Response(json.dumps({
        "likes":likes,
        }),mimetype='application/json')

#-----------------------------------后台管理API---------------------------------------
@api.route('/comments/<int:id>/', methods=["GET","DELETE"])
#@admin_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(comment)
        db.session.commit()
        return jsonify({
            'deleted': comment.id
        }), 200

