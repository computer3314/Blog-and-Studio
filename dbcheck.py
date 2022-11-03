import time
import logging
import random
from camera.models import Camera,Move,File
from django.conf import settings
import django.db

logger = logging.getLogger('django.db.backends')
#DB檢查器

def db_retry(fn, timeout=None):
    """Call fn with no arguments. If OperationalError exception, make retries until timeout has passed"""
    timeout = timeout or settings.DATABASES['default'].get('OPTIONS', dict()).get('timeout', 5)
    now = time.time()
    give_up_time = now + timeout
    retries = 0
    while now < give_up_time:
        now = time.time()
        try:
            result = fn
            if retries:
                logger.warning(f'db_retry: Succeeded after {retries} retries')
            return result
        except django.db.OperationalError as exception:
            msg = str(exception)
            if 'locked' in msg:  # pragma: no cover
                retries += 1
                wait_time = random.uniform(1, timeout / 10)
                logger.warning(f'db_retry: {msg}: Retrying after {wait_time} seconds')
                django.db.close_old_connections()
                time.sleep(wait_time)
            else:  # pragma: no cover
                logger.exception(f'db_retry: {msg}: Giving up')
                raise