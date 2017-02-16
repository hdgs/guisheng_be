from .. import rds
from .. import app
from .. import make_celery
import os

celery = make_celery(app)

@celery.task(name='delete_hottags')
def delete_hottags():
    rds.flushdb()
    rds.set("hi",1)
    rds.save()
