from .. import rds
from .. import app
from .. import make_celery
import os

celery = make_celery(app)

@celery.task(name='restart_hottags_redis')
def restart_hottagss_redis():
    rds.flushdb()
    rds.save()
