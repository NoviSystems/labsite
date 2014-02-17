from core_settings import *

########## CELERY SETTINGS ############

# BROKER_HOST = "localhost"
# BROKER_PORT = 5672
# BROKER_VHOST = "lab_vhost"
# BROKER_PASSWORD = "BN4bj1ptqlVx"
# BROKER_USER = "labuser"
BROKER_URL = 'amqp://labuser:BN4bj1ptqlVx@localhost:5672/lab_vhost'
CELERY_TIMEZONE = 'America/New_York'
CELERY_ENABLE_UTC = True
CELERYBEAT_SCHEDULE = {
    'reconcile_db_with_gh-every-1-minutes': {
        'task':'worklog.tasks.reconcile_db_with_gh',
        'schedule':timedelta(hours=1),
        'args': (16, 16)
    },
}
#######################################

WORKLOG_SEND_REMINDERS = False

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {  
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'stag_lab',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'stag_lab',
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
