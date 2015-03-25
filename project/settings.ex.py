
from labsite.settings_core import *
from datetime import timedelta

SECRET_KEY = 'xz#=4k+4we__68ge_i6v_e5v^+km*p+j=+8qjcq(ox%qle!@k*'


ALLOWED_HOSTS = ['*']

DEBUG = True

TEMPLATE_DEBUG = DEBUG

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
}
