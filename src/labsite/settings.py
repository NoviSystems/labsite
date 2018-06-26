"""
Django settings

Generated by 'django-admin startproject' using Django 1.11, and customized a
bit to add a logging config and a few other tweaks.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
from datetime import timedelta

from celery.schedules import crontab
from django.contrib.messages import DEFAULT_TAGS
from django.contrib.messages import constants as messages
from django.urls import reverse_lazy
from environ import Env


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def path(value):
    # Builds absolute paths relative to BASE_DIR
    return os.path.abspath(os.path.join(BASE_DIR, value))


# Base directory for configuration files
LABSITE_CONF = os.path.abspath(os.environ['LABSITE_CONF'])


# Read in environment variables. Default values should be secure.
env = Env(
    DEBUG=(bool, False),
    SECRET_KEY=str,
    ALLOWED_HOSTS=list,
    SITE_URL=(str, 'http://localhost'),

    DATABASE_URL=str,
    BROKER_URL=str,

    WORKLOG_SEND_REMINDERS=bool,

    FOODAPP_SEND_INVOICE_REMINDERS=bool,
    STRIPE_API_SECRET_KEY=str,
    STRIPE_API_PUBLISHABLE_KEY=str,

    SENTRY_DSN=(str, ''),
)
env.read_env(os.path.join(LABSITE_CONF, 'labsite.env'))


# Authentication
AUTH_USER_MODEL = 'auth.User'

LOGIN_URL = reverse_lazy('login')

LOGOUT_URL = reverse_lazy('logout')

LOGIN_REDIRECT_URL = '/'


# Authentication Backends
# https://docs.djangoproject.com/en/1.11/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

SECRET_KEY = env('SECRET_KEY')

# With DEBUG off, Django checks that the Host header in requests matches one of
# these. If you turn off DEBUG and you're suddenly getting HTTP 400 Bad
# Request responses, you need to add the host names to this list
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',

    'raven.contrib.django.raven_compat',
    'template_forms',
    'rest_framework',
    'registration',
    'registration_invite',
    'rangefilter',

    'labsite.accounting',
    'labsite.foodapp',
    'labsite.worklog',
    'labsite.utils',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'labsite.urls'

WSGI_APPLICATION = 'labsite.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path('templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'labsite.utils.context_processors.navbar_context',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'


DEFAULT_FROM_EMAIL = 'webmaster@lab.oscar.ncsu.edu'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    # fail if no DATABASE_URL - don't use a default value
    'default': env.db(),
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    path('static')
]


# Messages - tags compatible w/ bootstrap and django admin styles
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-debug %s' % DEFAULT_TAGS[messages.DEBUG],
    messages.INFO: 'alert-info %s' % DEFAULT_TAGS[messages.INFO],
    messages.SUCCESS: 'alert-success %s' % DEFAULT_TAGS[messages.SUCCESS],
    messages.WARNING: 'alert-warning %s' % DEFAULT_TAGS[messages.WARNING],
    messages.ERROR: 'alert-danger %s' % DEFAULT_TAGS[messages.ERROR],
}


# celery
BROKER_URL = env('BROKER_URL')

CELERY_TIMEZONE = 'America/New_York'

CELERY_ENABLE_UTC = True

CELERYBEAT_SCHEDULE = {
    # worklog
    'reconcile_db_with_gh-every-1-hours': {
        'task': 'worklog.tasks.reconcile_db_with_gh',
        'schedule': timedelta(hours=1),
        'args': (16, 16)
    },
    'send_reminder_email-every-1-days': {
        'task': 'worklog.tasks.send_reminder_emails',
        'schedule': crontab(hour=17, minute=0, day_of_week=[1, 2, 3, 4, 5]),
    },
    'generate_invoice_email-every-1-days': {
        'task': 'worklog.tasks.generate_invoice_email',
        'schedule': crontab(hour=2, minute=0, day_of_week=[0, 1, 2, 3, 4, 5, 6]),
    },

    # foodapp
    'reset-rice-cooker': {
        'task': 'foodapp.tasks.reset_rice_cooker',
        'schedule': crontab(hour=0, minute=1, day_of_week=[0, 1, 2, 3, 4, 5, 6]),
    },
    'nightly-invoicing': {
        'task': 'foodapp.tasks.create_invoices',
        'schedule': crontab(hour=0, minute=0),
    },
    'weekly-billing': {
        'task': 'foodapp.tasks.send_invoice_notifications',
        'schedule': crontab(hour=17, minute=0, day_of_week=[6]),
    },
}


# django-rest-framework
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework_filters.backends.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'PAGINATE_BY': None,
}


# django-registration
ACCOUNT_ACTIVATION_DAYS = 7

REGISTRATION_OPEN = True


# Worklog
WORKLOG_SEND_REMINDERS = env('WORKLOG_SEND_REMINDERS')

WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER = 4

# Foodapp
FOODAPP_SEND_INVOICE_REMINDERS = env('FOODAPP_SEND_INVOICE_REMINDERS')

STRIPE_API_SECRET_KEY = env('STRIPE_API_SECRET_KEY')
STRIPE_API_PUBLISHABLE_KEY = env('STRIPE_API_PUBLISHABLE_KEY')

# Labsite
SITE_URL = env('SITE_URL')

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


# Sentry/Raven
# To support sentry logging, set the DSN in your .env file. You will need an
# account on a sentry server and create a project to get a DSN.
#
# You will also need to install the "raven" package in your virtualenv
# (remember to add it to your requirements.in)
#
# Installing the raven_compat app will log all Django request handling
# exceptions (500 errors)
#
# You may also wish to install the raven logger to capture logging warnings
# or errors. Simply install a handler with class
# 'raven.contrib.django.raven_compat.handlers.SentryHandler' and configure a
# logger to use it.
#
# See https://docs.sentry.io/clients/python/integrations/django/
if env('SENTRY_DSN'):
    import raven

    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

    RAVEN_CONFIG = {
        'dsn': env('SENTRY_DSN'),
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir))
    }


# Our preferred logging configuration.
# Django takes the LOGGING setting and passes it as-is into Python's
# logging dict-config function (logging.config.dictConfig())
# For information about how Python's logging facilities work, see
# https://docs.python.org/3.5/library/logging.html
#
# The brief 3-paragraph summary is:
# Loggers form a tree hierarchy. A log message is emitted to a logger
# somewhere in this tree, and the hierarchy is used to determine what to do
# with the message.
#
# Each logger may have a level. A message also has a level. A message is
# emitted if its level is greater than its logger's level, or in case its
# logger doesn't have a level, the next one down in the hierarchy (repeat all
# the way until it hits the root, which always has a level). Note that the
# first logger with a level is the ONLY logger whose level is used in this
# decision.
#
# Each logger may have zero or more handlers, which determine what to do with
# a message that is to be emitted (e.g. print it, email it, write to a file). A
# message that passes the level test travels down the hierarchy, being sent
# to each handler at each logger, until it reaches the root logger or a
# logger marked with propagate=False. Each handler may do level checks or
# additional filtering of its own.
#
#
# Typically, you will want to log messages within your application under your
# own logger or a sublogger for each component, often named after the modules,
# such as "myapp.views",  "myapp.models", etc. Then you can customize what to
# do with messages from different components of your app.
#
# You don't need to declare a loggers in the config; they are created
# implicitly with no level and no handlers when calling logging.getLogger()
#
#
# Note: if you are getting a lot of DEBUG or INFO level log messages from
# third party libraries, a good change to make is:
# * Set the root logger level to "WARNING"
# * Add a logger for your project and set its level to DEBUG or INFO
# * Use your logger or a sub-logger of it throughout your project
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s [%(name)s] "
                      "%(message)s",
            "log_colors": {"DEBUG": "cyan",
                           "INFO": "white",
                           "WARNING": "yellow",
                           "ERROR": "red",
                           "CRITICAL": "white,bg_red",
                           }
        },
        "nocolor": {
            "format": "%(asctime)s %(levelname)-8s [%(name)s] "
                      "%(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S',
        },
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "color" if sys.stderr.isatty() else "nocolor",
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    "loggers": {
        "django": {
            # Django logs everything it does under this handler. We want
            # the level to inherit our root logger level and handlers,
            # but also add a mail-the-admins handler if an error comes to this
            # point (Django sends an ERROR log for unhandled exceptions in
            # views)
            "handlers": ["mail_admins"],
            "level": "NOTSET",
        },
        "django.db": {
            # Set to DEBUG to see all database queries as they happen.
            # Django only sends these messages if settings.DEBUG is True
            "level": "INFO",
        },
        "py.warnings": {
            # This is a built-in Python logger that receives warnings from
            # the warnings module and emits them as WARNING log messages*. By
            # default, this logger prints to stderr. We override that here so
            # that it simply inherits the root logger's handlers
            #
            # * Django enables this behavior by calling
            #   https://docs.python.org/3.5/library/logging.html#logging.captureWarnings
        }
    },
    "root": {
        "handlers": ["stderr"],
        "level": "INFO",
    }
}
