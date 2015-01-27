
from fabric.api import task, execute, sudo, prompt
from fabric.contrib import files
from fabtools import require
from fabtools import user
import fabtools

from django.utils.crypto import get_random_string


PG_VERSION = '9.4'


__all__ = [
    'application', 'broker', 'database', 'all',
]


@task
def base():
    fabtools.ssh.harden()
    fabtools.systemd.restart('sshd')

    # enable selinux
    # ...

    require.package('ntp')
    require.service.enabled('ntpd')
    sudo('ntpdate pool.ntp.org')

    require.package('firewalld')
    require.service.enabled('firewalld')


@task
def application():
    secrets_context = {
        'SECRET_KEY': get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'),
        'sentry_dsn': prompt("Sentry DSN:"),
    }

    execute(base)

    require.user('labuser', home='/opt/lab/', shell='/bin/bash')
    require.postgres.packages(PG_VERSION)

    require.packages([
        'nginx',
        'supervisord',
    ])

    sudo('firewall-cmd --add-port=80/tcp')
    sudo('firewall-cmd --add-port=80/tcp --permanent')
    sudo('firewall-cmd --add-port=443/tcp')
    sudo('firewall-cmd --add-port=443/tcp --permanent')

    with user.masquerade('labuser'):
        require.directory('log')
        require.file('log/celeryd.log')
        require.file('log/celerybeat.log')
        require.file('log/deployment.log')

        require.directory('backups')

        require.python.virtualenv('venv')

        files.upload_template('labsite/secrets.tmpl.py', 'secrets.py', use_sudo=True, context=secrets_context)


@task
def broker():
    execute(base)

    require.package('redis')

    sudo('firewall-cmd --add-port=6379/tcp')
    sudo('firewall-cmd --add-port=6379/tcp --permanent')


@task
def database(name='default', db_version=None):
    from django.conf import settings
    db = settings.DATABASES[name]

    execute(base)

    # initialize postgres
    pg_service = require.postgres._service_name(PG_VERSION)

    require.postgres.server(PG_VERSION)
    require.service.started(pg_service)
    require.service.enabled(pg_service)
    require.postgres.listening_on('*')

    # This should be more secure, but it's on the private network currently so ehhhh
    require.postgres.hba_rule('host', db['NAME'], db['USER'], '', 'trust')

    sudo('firewall-cmd --add-port=5432/tcp')
    sudo('firewall-cmd --add-port=5432/tcp --permanent')

    require.postgres.user(db['USER'])
    require.postgres.database(db['NAME'], db['USER'], 'no-superuser', 'no-createdb', 'no-createrole')


@task(default=True)
def all():
    execute(application, roles=['application'])
    execute(broker, roles=['broker'])
    execute(database, roles=['database'])
