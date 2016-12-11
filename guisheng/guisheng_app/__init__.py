# coding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension
from config import config
import flask.ext.whooshalchemy as whooshalchemy
import redis
from celery import Celery


app = Flask(__name__)
"""
config
 -- 'default': DevelopmentConfig
 -- 'develop': DevelopmentConfig
 -- 'testing': TestingConfig
 -- 'production': ProductionConfig
    you can edit this in config.py
"""
config_name = 'default'
app.config.from_object(config[config_name])
config[config_name].init_app(app)
toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
moment = Moment(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

#redis site
rds = redis.StrictRedis(host='localhost', port=6380, db=0)

#to search
from .models import News,Article,Picture,Interaction,Tag
whooshalchemy.whoosh_index(app, News)
whooshalchemy.whoosh_index(app, Article)
whooshalchemy.whoosh_index(app, Picture)
whooshalchemy.whoosh_index(app, Interaction)
whooshalchemy.whoosh_index(app, Tag)

# admin site
from admin import views


"""
blueprint
you can register a <blueprint> by run:
 -- mana blueprint <blueprint>
under app folder
"""
from main import main
app.register_blueprint(main, url_prefix='/main')

from auth import auth
app.register_blueprint(auth, url_prefix="/auth")

from api_1_0 import api
app.register_blueprint(api, url_prefix="/api/v1.0")

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
