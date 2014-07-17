
from core_settings import *
from celery.schedules import crontab


ADMINS = (
    ('John Bass', 'jbass@ncsu.edu'),
)

SITE_URL = "lab.oscar.ncsu.edu"

SECRET_KEY = open(os.path.join(SETTINGS_DIR, 'secret_key')).read()

DEBUG = False

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'prod_lab',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'prod_lab',
        'PASSWORD': '',
        'HOST': 'postgres92.oscar.ncsu.edu',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

days_of_week_map = {
    'everyday': [0, 1, 2, 3, 4, 5, 6],
    'weekdays': [1, 2, 3, 4, 5],
}

# CELERY SETTINGS
BROKER_URL = 'qpid://qpid-1.oscar.ncsu.edu:5672/'
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
    'generate_timesheets-every-1-days': {
        'task': 'worklog.tasks.generate_timesheets',
        'schedule': crontab(hour=2, minute=0, day_of_week=days_of_week_map['everyday']),
    },
    'generate_invoice_email-every-1-days': {
        'task': 'worklog.tasks.generate_invoice_email',
        'schedule': crontab(hour=2, minute=0, day_of_week=days_of_week_map['everyday']),
    },
}
