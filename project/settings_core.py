"""
Django settings for labsite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from __future__ import absolute_import
import os
import socket
from project.secrets import *
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages import constants as messages

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


SITE_URL = socket.gethostname()

ALLOWED_HOSTS = ['.oscar.ncsu.edu']


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True


DEFAULT_FROM_EMAIL = 'webmaster@lab.oscar.ncsu.edu'


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.forms',
    'template_forms',
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'rangefilter',
    'accounts',
    'itng.common',
    'itng.registration.backends.invite',
    'worklog',
    'foodapp',
    'accounting',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


MEDIA_URL = ''

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../media-root'))


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'

STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../static-root'))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'itng.common.context_processors.debug',
                'project.context_processors.navbar_context',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


# Messages - use tags that are compatible w/ both django's admin and bootstrap alerts
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-debug debug',
    messages.INFO: 'alert-info info',
    messages.SUCCESS: 'alert-success success',
    messages.WARNING: 'alert-warning warning',
    messages.ERROR: 'alert-danger error',
}

# CELERY SETTINGS
CELERY_TIMEZONE = 'America/New_York'

CELERY_ENABLE_UTC = True


# WORKLOG SETTINGS
WORKLOG_SEND_REMINDERS = False

WORKLOG_SEND_REMINDERS_HOUR = 17

WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER = 4

# FOODAPP SETTINGS
FOODAPP_SEND_INVOICE_REMINDERS = False

FOODAPP_SEND_REMINDERS_HOUR = 17

FOODAPP_SEND_REMINDERS_AFTER = 3

# DJANGO REGISTRATION SETTINGS
ACCOUNT_ACTIVATION_DAYS = 7

REGISTRATION_OPEN = True

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

RAVEN_CONFIG = {
    'dsn': SENTRY_DSN
}


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework_filters.backends.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': None,
}

LABSITE_APPS = [
    {
        'app_name': 'worklog',
        'display_name': "Worklog",
        'style': 'danger',
        'icon': 'fa-flask',
        'url': reverse_lazy('worklog:home'),
    },
    {
        'app_name': 'accounting',
        'display_name': "Accounting",
        'style': 'warning',
        'icon': 'fa-line-chart',
        'url': reverse_lazy('accounting:home'),
    },
    {
        'app_name': 'foodapp',
        'display_name': "Food App",
        'style': 'success',
        'icon': 'fa-beer',
        'url': reverse_lazy('foodapp:home'),
    },
]
