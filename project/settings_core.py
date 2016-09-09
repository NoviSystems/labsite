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
    'raven.contrib.django.raven_compat',
    'rest_framework',
    'accounts',
    'itng.common',
    'itng.registration.backends.invite',
    'itng.registration.templates',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'itng.registration.templates.context_processors.auth_base',
                'project.context_processors.navbar_context',
            ],
        },
    },
]

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
        'color': '#D9534F',
        'font_image': 'fa-flask',
        'url': reverse_lazy('worklog:home'),
        'new_tab': 'false',
    },
    {
        'app_name': 'accounting',
        'display_name': "Accounting",
        'color': '#F0AD4E',
        'font_image': 'fa-line-chart',
        'url': reverse_lazy('accounting:home'),
        'new_tab': 'false',
    },
    {
        'app_name': 'foodapp',
        'display_name': "Food App",
        'color': '#5CB85C',
        'font_image': 'fa-beer',
        'url': reverse_lazy('foodapp:home'),
        'new_tab': 'false',
        'margin': '30',
    },
    {
        'app_name': 'KABA',
        'display_name': "KABA",
        'color': '#428BCA',
        'font_image': 'fa-clock-o',
        'url': 'https://kaba.oit.ncsu.edu/WebTimeClock/main/index.jsp?actionEvent=cmd://startdialog',
        'new_tab': 'true',
    }
]
