
from app import app
from app import rds
import os

celery = make_celery(app)

@celery.task(name='restart_hottags_redis')
def restart_hottagss_redis():
    # 清空所有热门标签
    rds.flushdb()
    rds.save()
