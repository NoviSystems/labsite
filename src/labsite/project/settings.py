'''
-*- Development Settings -*-

This file contains development-specific settings. You can run the django
development server without making any changes to this file, but it's not
suitable for production. The production settings files are located under
the './deploy' directory.
'''
import socket

from .common_settings import *  # noqa


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_URL = socket.gethostname()
