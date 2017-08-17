#coding: utf-8

# config



# project base path
import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

"""
common configuration
 -- SECRET_KEY: secret key
 -- SQLALCHEMY_COMMIT_ON_TEARDOWN: True

 -- SQLALCHEMY_RECORD_QUERIES:
    -- Can be used to explicitly disable or enable query recording.
       Query recording automatically happens in debug or testing mode.

 -- SQLALCHEMY_TRACK_MODIFICATIONS:
    -- If set to True, Flask-SQLAlchemy will track modifications of
       objects and emit signals.
       The default is None, which enables tracking but issues a warning that
       it will be disabled by default in the future.
       This requires extra memory and should be disabled if not needed.

 more configuration keys please see:
  -- http://flask-sqlalchemy.pocoo.org/2.1/config/#configuration-keys
"""
class Config:
    """common configuration"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = os.path.join(basedir,"pics")
    ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])
    WHOOSH_BASE = os.path.join(basedir,"whoosh_index")
    CELERY_BROKER_URL = 'redis://{}:6380/1'.format(os.environ.get("BROKER_URI"))
    CELERY_RESULT_BACKEND = 'redis://{}:6381/1'.format(os.environ.get("BACKEND_URI"))
    CELERYBEAT_SCHEDULE = {
        'restart_redis_every_month': {
        'task': 'delete_hottags',
        'schedule': timedelta(seconds=2592000)
        },
    }

    @staticmethod
    def init_app(app):
        pass

"""
development configuration
 -- DEBUG: debug mode
 -- SQLALCHEMY_DATABASE_URI:
    -- The database URI that should be used for the connection.

"""
class DevelopmentConfig(Config):
    """development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URI')
#    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


# production configuration
class ProductionConfig(Config):
    """production configuration"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data.sqlite")
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

"""
testing configuration
 -- TESTING: True
 -- WTF_CSRF_ENABLED:
    -- in testing environment, we don't need CSRF enabled
"""
class TestingConfig(Config):
    """testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "data-test.sqlite")
    WTF_CSRF_ENABLED = False


config = {
    "develop": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

