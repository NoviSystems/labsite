
from labsite.settings_core import *
from datetime import timedelta
from celery.schedules import crontab

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
    # worklog
    'reconcile_db_with_gh-every-1-minutes': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(minutes=1),
        'args': (16, 16)
    },

    # foodapp
    'reset-rice-cooker': {
        'task': 'foodapp.tasks.reset_rice_cooker',
        'schedule': crontab(hour=0, minute=1, day_of_week=[0, 1, 2, 3, 4, 5, 6]),
    },
}

# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = False
