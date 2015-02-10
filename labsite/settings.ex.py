
from labsite.settings_core import *

SECRET_KEY = 'xz#=4k+4we__68ge_i6v_e5v^+km*p+j=+8qjcq(ox%qle!@k*'

# Celery broker URL
# BROKER_URL = 'qpid://qpid-1.oscar.ncsu.edu:5672/'


ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<username>_lab',
        'USER': '<username>',
        'PASSWORD': '',
        'HOST': '192.168.10.11',
        'PORT': '',
    }
}
