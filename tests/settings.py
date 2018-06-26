from labsite.settings import *  # noqa
from labsite.settings import LOGGING


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
        'TEST': {
            'NAME': 'test.sqlite3',
        },
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = True

WORKLOG_SEND_REMINDERS_HOUR = 18

WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER = 4


# Logging
LOGGING['root']['level'] = 'ERROR'
