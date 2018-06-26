#!/usr/bin/env python
import os
import sys
from argparse import ArgumentParser


DEV_SETTINGS = """\
from labsite.settings import *  # noqa


# Prevent accidental sending of emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
"""


PROD_SETTINGS = """\
from labsite.settings import *  # noqa


ADMINS = [
    # ('Admin Name', 'admin.email@example.com'),
]

# To force SSL if the upstream proxy server doesn't do it for us, set to True
SECURE_SSL_REDIRECT = False


# manifest storage is useful for its automatic cache busting properties
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
"""


DEV_ENVFILE = """\
# Environment settings suitable for development.
# Note that these settings are *not* secure.

DEBUG=true
SECRET_KEY="not-so-secret"
ALLOWED_HOSTS="*"
SITE_URL="http://localhost"

DATABASE_URL="sqlite:///db.sqlite3"
DRAMATIQ_BROKER_URL="redis://"
ELASTICSEARCH_URL="http://localhost:9200/"

# Adds sentry error reporting. See labsite.settings for details.
# SENTRY_DSN=""
"""

PROD_ENVFILE = """\
DEBUG=false
SECRET_KEY=""
ALLOWED_HOSTS=""
SITE_URL=""

DATABASE_URL=""
DRAMATIQ_BROKER_URL=""
ELASTICSEARCH_URL=""

# Adds sentry error reporting. See labsite.settings for details.
# SENTRY_DSN=""
"""


def init(args=None):
    parser = ArgumentParser(description='Initialize a new configuration directory.')
    parser.add_argument('directory', type=str)
    parser.add_argument('--dev', dest='dev', action='store_true', default=False,
                        help="Use settings more suitable for development.")

    options = parser.parse_args(args)

    directory = os.path.abspath(options.directory)
    settings = os.path.join(directory, 'settings.py')
    dotenv = os.path.join(directory, 'labsite.env')

    if not os.path.isdir(directory):
        parser.error(f"Directory '{directory}' does not exist.")
    if os.path.exists(settings):
        parser.error(f"A file already exists at '{settings}'.")
    if os.path.exists(dotenv):
        parser.error(f"A file already exists at '{dotenv}'.")

    with open(settings, 'w') as file:
        file.write(DEV_SETTINGS if options.dev else PROD_SETTINGS)
        print('labsite settings created...')
    with open(dotenv, 'w') as file:
        file.write(DEV_ENVFILE if options.dev else PROD_ENVFILE)
        print('labsite environment file created...')
    print('\nDone!')


def main(args=None):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('LABSITE_CONF', '.')
    sys.path.insert(0, os.environ['LABSITE_CONF'])

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
