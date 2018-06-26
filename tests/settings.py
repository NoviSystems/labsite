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


# Logging
LOGGING['root']['level'] = 'ERROR'
