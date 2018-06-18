'''
-*- Production Settings -*-

This file contains production-specific settings. Complete the deployment
checklist and make any necessary changes.
https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
'''

from ..common_settings import *  # noqa
from ..common_settings import path


SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True


# manifest storage is useful for its automatic cache busting properties
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = path('../static-root')
