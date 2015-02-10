
from fabric.api import env, task
from fabric.contrib import django
import json

from labsite.fabfile import *


# turn fabric helper method into an actual task.
settings = task(name='settings')(django.settings_module)


def load_environ_config():
    with open('environ.json') as configfile:
        conf = json.load(configfile)[env.environ]

        django.settings_module(conf['django_settings'])

        env.update(conf['env'])

        # for now, also use env to store other global state
        del conf['env']
        env.update(conf)


@task
def environ(environ):
    """
    Setup the environment that is being worked on.  [prod, stag, test, default]
    """
    env.environ = environ
    load_environ_config()


# set default environ and load
if not hasattr(env, 'environ'):
    env.environ = 'default'

load_environ_config()
