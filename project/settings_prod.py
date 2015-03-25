
from labsite.settings_core import *
from celery.schedules import crontab


ADMINS = (
    ('John Bass', 'jbass@ncsu.edu'),
)

SITE_URL = "lab.oscar.ncsu.edu"

DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lab_prod',
        'USER': 'lab_prod',
        'HOST': 'lab-db.oscar.priv',
    }
}

days_of_week_map = {
    'everyday': [0, 1, 2, 3, 4, 5, 6],
    'weekdays': [1, 2, 3, 4, 5],
}

# CELERY SETTINGS
# BROKER_URL = 'qpid://qpid-1.oscar.ncsu.edu:5672//'
# BROKER_URL = 'amqp://labuser:BN4bj1ptqlVx@localhost:5672/lab_vhost'
BROKER_URL = 'redis://lab-broker.oscar.priv:6379/0'
# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS_DAY = days_of_week_map[WORKLOG_SEND_REMINDERS_DAYSOFWEEK]

CLEAR_REMINDERS_DAYSOFWEEK = days_of_week_map[WORKLOG_CLEAR_REMINDERS_DAYSOFWEEK]

CELERYBEAT_SCHEDULE = {
    'reconcile_db_with_gh-every-1-hours': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(hours=1),
        'args': (16, 16)
    },
    'send_reminder_email-every-1-days': {
        'task': 'worklog.tasks.send_reminder_emails',
        'schedule': crontab(hour=WORKLOG_SEND_REMINDERS_HOUR, minute=0, day_of_week=WORKLOG_SEND_REMINDERS_DAY),
    },
    'generate_invoice_email-every-1-days': {
        'task': 'worklog.tasks.generate_invoice_email',
        'schedule': crontab(hour=2, minute=0, day_of_week=days_of_week_map['everyday']),
    },
}
