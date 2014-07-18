"""
Django settings for labsite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from datetime import timedelta
import os
import socket
from secrets import *

SETTINGS_DIR = os.path.realpath(os.path.join(__file__, "../"))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


DEBUG = True

TEMPLATE_DEBUG = DEBUG


SITE_URL = socket.gethostname()

ALLOWED_HOSTS = ['.oscar.ncsu.edu']

SECRET_KEY = ''


DEFAULT_FROM_EMAIL = 'webmaster@lab.oscar.ncsu.edu'


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'discover_runner',
    'south',
    'worklog',
    'foodapp',
    'djcelery',
    'gunicorn',
    'rest_framework',
    'raven.contrib.django.raven_compat',
)

TEST_RUNNER = 'discover_runner.DiscoverRunner'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'labsite.urls'

WSGI_APPLICATION = 'labsite.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


MEDIA_URL = ''

MEDIA_ROOT = os.path.join(BASE_DIR, 'media-root')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static-root')

STATICFILES_DIRS = (
    # "/opt/lab/labsite/foodapp/static/",
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages'
)


# CELERY SETTINGS

# BROKER_HOST = "localhost"
# BROKER_PORT = 5672
# BROKER_VHOST = "lab_vhost"
# BROKER_PASSWORD = "BN4bj1ptqlVx"
# BROKER_USER = "labuser"
CELERY_TIMEZONE = 'America/New_York'
CELERY_ENABLE_UTC = True
CELERYBEAT_SCHEDULE = {
    'reconcile_db_with_gh-every-1-minutes': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(hours=1),
        'args': (16, 16)
    },
}
import djcelery
djcelery.setup_loader()

# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = True
WORKLOG_SEND_REMINDERS_HOUR = 17
WORKLOG_SEND_REMINDERS_DAYSOFWEEK = "weekdays"
WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER = 4
WORKLOG_CLEAR_REMINDERS_DAYSOFWEEK = "weekdays"
WORKLOG_CLEAR_REMINDERS_HOUR = 2
WORKLOG_REMINDER_EMAIL_LINK_URLBASE = "https://lab-prod.oscar.ncsu.edu"

#######################################

LOGIN_REDIRECT_URL = '/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': None
}

RAVEN_CONFIG = {
    'dsn': SENTRY_DSN
}
