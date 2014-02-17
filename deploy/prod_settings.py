from core_settings import *
from celery.schedules import crontab

# DONT PROD ME BRO

########## CELERY SETTINGS ############

# BROKER_HOST = "localhost"
# BROKER_PORT = 5672
# BROKER_VHOST = "lab_vhost"
# BROKER_PASSWORD = "BN4bj1ptqlVx"
# BROKER_USER = "labuser"
BROKER_URL = 'amqp://labuser:BN4bj1ptqlVx@localhost:5672/lab_vhost'
CELERY_TIMEZONE = 'America/New_York'
CELERY_ENABLE_UTC = True

# Email reminders are typically sent every weekday
days_of_week_mapper = {
    'everyday': [0,1,2,3,4,5,6],
    'weekdays': [1,2,3,4,5],
    }
WORKLOG_SEND_REMINDERS_DAY = days_of_week_mapper[WORKLOG_SEND_REMINDERS_DAYSOFWEEK]

# The time and days to clear reminder records from the database.
CLEAR_REMINDERS_DAYSOFWEEK = days_of_week_mapper[WORKLOG_CLEAR_REMINDERS_DAYSOFWEEK]

CELERYBEAT_SCHEDULE = {
    'reconcile_db_with_gh-every-1-hours': {
        'task':'worklog.tasks.reconcile_db_with_gh',
        'schedule':timedelta(hours=1),
        'args': (16, 16)
    },
    'send_reminder_email-every-1-days': {
        'task':'worklog.tasks.send_reminder_emails',
        'schedule':crontab(hour=WORKLOG_SEND_REMINDERS_HOUR, minute=0, day_of_week=WORKLOG_SEND_REMINDERS_DAY),
    },
    'generate_timesheets-every-1-days': {
        'task':'worklog.tasks.generate_timesheets',
        'schedule':crontab(hour=2, minute=0, day_of_week=days_of_week_mapper['everyday']),
    },
    'generate_invoice_email-every-1-days': {
        'task':'worklog.tasks.generate_invoice_email',
        'schedule':crontab(hour=2, minute=0, day_of_week=days_of_week_mapper['everyday']),
    },
    'clear_expired_reminder_records-every-1-days': {
        'task':'worklog.tasks.clear_expired_reminder_records',
        'schedule':crontab(hour=WORKLOG_CLEAR_REMINDERS_HOUR, minute=0, day_of_week=CLEAR_REMINDERS_DAYSOFWEEK),
    },
}
#######################################

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
