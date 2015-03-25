
from labsite.settings_core import *
from datetime import timedelta

SITE_URL = "lab-stag.oscar.ncsu.edu"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lab_stag',
        'USER': 'lab_stag',
        'HOST': 'lab-db.oscar.priv',
    }
}


# CELERY SETTINGS
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
