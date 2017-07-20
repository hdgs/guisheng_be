# coding: utf-8

import json

from flask import request,jsonify,Response
from flask_login import login_user, logout_user, current_user, login_required

from . import api
from guisheng_app import db
from guisheng_app.decorators import admin_required
from guisheng_app.models import SpProject,ChildTopic,Role,User,News,Picture,Tag,PostTag,Image,Collect


#-----------------------------------后台管理API---------------------------------------
#ToDo
#1,Modify special project
#2,Add a ChildTopic to a SpProject
#3,Create an Article(News) OR Under that project one of project's ChildTopic
#4,Create a Pictures Under that project one of project's ChildTopic
#5,Give the list of Projects and its childTopic and childTopic's articles and pics;

@api.route('/spproj/',methods = ['POST'])
@admin_required
def add_special_proj():
	if request.method == 'POST':
		name = request.get_json().get('project_name')
		project = SpProject()
		project.project_name = name
		db.session.add(project)
		db.session.commit()
	    proj_id = project.id 
		
		return jsonify({
			'id':proj_id
		}),201


@api.route()