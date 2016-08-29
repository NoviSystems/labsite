
from __future__ import absolute_import
from project.settings_core import *
from datetime import timedelta
from celery.schedules import crontab


ADMINS = (
    # ('John Bass', 'jbass@ncsu.edu'),
)

SITE_URL = "lab.oscar.ncsu.edu"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lab_prod',
        'USER': 'lab_prod',
        'HOST': 'lab-db.oscar.priv',
    }
}

# CELERY SETTINGS
BROKER_URL = 'redis://lab-broker.oscar.priv:6379/0'

CELERYBEAT_SCHEDULE = {
    # worklog
    'reconcile_db_with_gh-every-1-hours': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(hours=1),
        'args': (16, 16)
    },
    'send_reminder_email-every-1-days': {
        'task': 'worklog.tasks.send_reminder_emails',
        'schedule': crontab(hour=17, minute=0, day_of_week=[1, 2, 3, 4, 5]),
    },
    'generate_invoice_email-every-1-days': {
        'task': 'worklog.tasks.generate_invoice_email',
        'schedule': crontab(hour=2, minute=0, day_of_week=[0, 1, 2, 3, 4, 5, 6]),
    },

    # foodapp
    'reset-rice-cooker': {
        'task': 'foodapp.tasks.reset_rice_cooker',
        'schedule': crontab(hour=0, minute=1, day_of_week=[0, 1, 2, 3, 4, 5, 6]),
    },
    'weekly_billing': {
        'task': 'foodapp.tasks.send_invoice_notifications',
        'schedule': crontab(hour=0, minute=0, day_of_week=[6]),
    },
}

# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = True

# FOODAPP SETTINGS
FOODAPP_SEND_INVOICE_REMINDERS = True
