
from __future__ import absolute_import
from project.settings_core import *
from datetime import timedelta
from celery.schedules import crontab

SECRET_KEY = 'xz#=4k+4we__68ge_i6v_e5v^+km*p+j=+8qjcq(ox%qle!@k*'


ALLOWED_HOSTS = ['*']

DEBUG = True

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': '<username>_lab',
        # 'USER': '<username>',
        'HOST': '192.168.10.10',
    }
}

# CELERY SETTINGS
# BROKER_URL = 'amqp://<username>:<password>@dev-mq.oscar.priv:5672/<vhost>'
BROKER_URL = 'redis://192.168.10.10:6379/0'

CELERYBEAT_SCHEDULE = {
    'reconcile_db_with_gh-every-1-minutes': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(hours=1),
        'args': (16, 16)
    },
    'reset-rice-cooker': {
        'task': 'foodapp.tasks.reset_rice_cooker',
        'schedule': crontab(hour=0, minute=1, day_of_week=[0, 1, 2, 3, 4, 5, 6]),
    },
}
