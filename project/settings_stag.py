
from labsite.settings_core import *


DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lab_stag',
        'USER': 'lab_stag',
        'HOST': 'lab-db.oscar.priv',
    }
}


# CELERY SETTINGS
# BROKER_URL = 'django://qpid-1.oscar.ncsu.edu:5672/'
# CELERY_RESULT_BACKEND='qpid'
# BROKER_URL = 'qpid://qpid-1.oscar.ncsu.edu:5672//'
# BROKER_URL = 'amqp://labuser:BN4bj1ptqlVx@localhost:5672/lab_vhost'
BROKER_URL = 'redis://lab-broker.oscar.priv:6379/1'
CELERYBEAT_SCHEDULE = {
    'reconcile_db_with_gh-every-1-minutes': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(minutes=1),
        'args': (16, 16)
    },
}

# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = False
