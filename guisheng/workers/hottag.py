from .guisheng_app import app
from guisheng_app import rds
import os

celery = make_celery(app)

@celery.task(name='restart_hottags_redis')
def restart_hottagss_redis():
    rds.flushdb()
    rds.save()
