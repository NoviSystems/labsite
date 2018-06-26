"""
WSGI config for labsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application


# By default, look for a settings module in the labsite config directory.
sys.path.insert(0, os.environ['LABSITE_CONF'])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()
