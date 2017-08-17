# coding: utf-8

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
from flask_debugtoolbar import DebugToolbarExtension
from config import config
import flask.ext.whooshalchemy as whooshalchemy
import redis
from celery import Celery


"""
config
 -- 'default': DevelopmentConfig
 -- 'develop': DevelopmentConfig
 -- 'testing': TestingConfig
 -- 'production': ProductionConfig
    you can edit this in config.py
"""
toolbar = DebugToolbarExtension()
db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

#redis site
rds = redis.StrictRedis(host=os.environ.get("BACKEND_URI"), port=6381, db=1)


def create_app(config_name=None, main=True):
    if config_name is None:
        config_name = 'default'
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    db.init_app(app)
    moment.init_app(app)
    toolbar.init_app(app)
    login_manager.init_app(app)

    # admin site
    from admin import views

    from main import main
    app.register_blueprint(main, url_prefix='/main')

    from auth import auth
    app.register_blueprint(auth, url_prefix="/auth")

    from api_1_0 import api
    app.register_blueprint(api, url_prefix="/api/v1.0")

    return app

app = create_app(config_name = 'default')

#to search
from .models import News,Article,Picture,Interaction,Tag
try:
    whooshalchemy.whoosh_index(app, News)
    whooshalchemy.whoosh_index(app, Article)
    whooshalchemy.whoosh_index(app, Picture)
    whooshalchemy.whoosh_index(app, Interaction)
    whooshalchemy.whoosh_index(app, Tag)
except:
    pass

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

