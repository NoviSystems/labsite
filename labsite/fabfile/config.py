
from fabric.api import task, prompt, env, sudo
from fabric.contrib import files
from fabtools.files import is_file
from fabtools import require
from fabtools import user

from django.utils.crypto import get_random_string
from functools import partial
import posixpath


__all__ = (
    'application_secrets', 'certify', 'recertify',
)


# @task
def secrets_context(**kwargs):
    def r(value):
        return value() if callable(value) else value

    defaults = {
        'SECRET_KEY':   partial(get_random_string, 50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'),
        'GITHUB_USER':  partial(prompt, "Worklog GitHub username:"),
        'GITHUB_PASS':  partial(prompt, "Worklog GitHub password:"),
        'SENTRY_DSN':   partial(prompt, "Sentry DSN:"),
    }
    return {key: r(kwargs.get(key, value)) for key, value in defaults.items()}


@task
def application_secrets(**kwargs):
    """
    """
    context = secrets_context(**kwargs)
    with user.masquerade('labuser'):
        files.upload_template('labsite/setup/secrets.tmpl.py', 'secrets.py', context=context)


@task
def certify(force=False):
    """
    Generates a self-signed server cert.
    """
    cert_dir = '/etc/nginx/certs/'
    paths = {
        'key': posixpath.join(cert_dir, 'server.key'),
        'crt': posixpath.join(cert_dir, 'server.crt'),
    }

    if not (is_file(paths['key']) and is_file(paths['crt'])) or force:
        require.directory(cert_dir, use_sudo=True)

        config = {'cn': env.host}
        config.update(paths)

        sudo(
            "openssl req -x509 -newkey rsa:2048 -nodes "
            "-keyout %(key)s -out %(crt)s -days 365 "
            "-subj '/CN=%(cn)s'" % config
        )


@task
def recertify():
    """
    Forces regeneration of self-signed server certs
    """
    certify(force=True)
