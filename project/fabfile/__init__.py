
from fabric.api import env, prompt
from prefab import environ
from prefab import secrets

from django.utils.crypto import get_random_string

from collections import OrderedDict
from functools import partial

__all__ = [
    'config', 'deploy', 'provision', 'vagrant',
]


PROJECT_NAME = 'labsite'
USERNAME = 'labuser'
PG_VERSION = '9.4'


secrets.register('application', OrderedDict([
        ('SECRET_KEY',  partial(get_random_string, 50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')),
        ('GITHUB_USER', partial(prompt, "Worklog GitHub username:")),
        ('GITHUB_PASS', partial(prompt, "Worklog GitHub password:")),
        ('SENTRY_DSN',  partial(prompt, "Sentry DSN:")),
        ('STRIPE_API_SECRET_KEY',  partial(prompt, "Stripe secret key:")),
        ('STRIPE_API_PUBLISHABLE_KEY',  partial(prompt, "Stripe publishable key:")),
    ])
)

env.forward_agent = True

# set default environ and load
if not hasattr(env, 'environ'):
    env.environ = 'default'

environ.load(env.environ)
