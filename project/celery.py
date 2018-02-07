from __future__ import absolute_import

import os
from celery import Celery
from environ import Env

from django.conf import settings

# set the default Django settings module for the 'celery' program.
envfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
if os.path.exists(envfile):
    Env.read_env(envfile)

app = Celery('labsite')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
