
from fabric.api import env, task
from fabric.contrib import django
from functools import partial

from labsite.fabfile import *


settings = task(django.settings_module)

env.forward_agent = True


@task
def environ(environ=None):
    """
    Setup the environment that is being worked on.  [prod, stag, test, default]
    """
    env.environ = environ

    # django settings
    if environ:
        django.settings_module('labsite.settings_%s' % environ)
    else:
        django.settings_module('labsite.settings')

    # connection settings
    if environ and environ != 'test':
        env.use_ssh_config = True
    else:
        env.user = 'vagrant'
        env.password = 'vagrant'

    # load roledefs
    env.roledefs = {
        'application': partial(_hosts, environ, 'application'),
        'broker': partial(_hosts, environ, 'broker'),
        'database': partial(_hosts, environ, 'database'),
    }


def _hosts(environ, role):
    defs = {
        'prod': {
            'application': ['lab-prod.oscar.priv', ],
            'broker': ['lab-prod.oscar.priv', ],
            'database': ['lab-prod.oscar.priv', ],
        },
        'stag': {
            'application': ['lab-stag.oscar.priv', ],
            'broker': ['lab-stag.oscar.priv', ],
            'database': ['lab-stag.oscar.priv', ],
        },
        'test': {
            'application': ['192.168.11.20', ],
            'broker': ['192.168.11.11', ],
            'database': ['192.168.11.10', ],
        }
    }.get(environ, {  # default/fallback lookup
        'application': ['192.168.10.20', ],
        'broker': ['192.168.10.11', ],
        'database': ['192.168.10.10', ],
    })

    return defs[role]
