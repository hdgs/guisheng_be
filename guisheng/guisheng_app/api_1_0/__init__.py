from flask import Blueprint

api = Blueprint('api',__name__)

from . import feed,everydaypic,pictures,news,articles,\
        interactions,profile,comments,light,authentication,user,collect,like
