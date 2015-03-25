
from fabric.api import task, roles, env, execute, cd, sudo
from fabric.contrib import files
from fabtools import require
from fabtools import postgres
from fabtools import python
from fabtools import user
from prefab import pipeline
from prefab import secrets
from prefab.utils import host_roles, role_hosts

import re

from project.fabfile import config
from project.fabfile import PG_VERSION


IP_ADDR = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')


__all__ = [
    'application', 'frontend', 'worker', 'broker', 'database', 'devel', 'all',
]


@task
@pipeline.once
def base():
    require.system.defaults()
    require.ssh.hardened()

    # selinux - reference:
    # http://wiki.centos.org/HowTos/SELinux
    sudo('setenforce 1')
    files.sed('/etc/selinux/config', r'^SELINUX=.*$', 'SELINUX=enforcing', use_sudo=True)

    require.package('ntp')
    require.service.enabled('ntpd')
    require.service.stopped('ntpd')
    sudo('ntpdate pool.ntp.org')
    require.service.started('ntpd')

    require.firewall.service()
    config.firewall()


@task
@pipeline.once
@pipeline.requires(base)
def application():
    # resolve secrets input as soon as possible
    secrets.context('application')

    require.user('labuser', home='/opt/lab/', shell='/bin/bash')
    require.postgres.packages(PG_VERSION)

    require.rpm.repository('epel')
    require.packages([
        'nginx',
        'supervisor',
        'git',
        'gcc',
    ])

    # nginx certs and SELinux rules
    require.python.pip()
    require.python.package('virtualenv', use_sudo=True)

    with user.masquerade('labuser'):
        require.directory('log')
        require.file('log/deployment.log')

        require.directory('backups')

        require.python.virtualenv('venv')

        execute(config.application_secrets)


@task
@roles('application')
@pipeline.once
@pipeline.requires(application)
def frontend():
    execute(config.certify)
    sudo('setsebool -P httpd_read_user_content 1')

    # We need to give the nginx server exec access to the labuser's home
    # directory. This is necessary so nginx has access to the static-root
    # and media-root directories.
    sudo('usermod -a -G labuser nginx')
    sudo('chmod g+x ~labuser')


@task
@roles('application')
@pipeline.once
@pipeline.requires(application)
def worker():
    with user.masquerade('labuser'):
        require.directory('log')
        require.file('log/celeryd.log')
        require.file('log/celerybeat.log')


@task
@roles('broker')
@pipeline.requires(base)
def broker():
    require.rpm.repository('epel')
    require.package('redis')

    require.service.started('redis')
    require.service.enabled('redis')

    # TODO: formalize this a la postgres
    # require.redis.listening_on('0.0.0.0')
    files.sed('/etc/redis.conf', r'^(\s*)?bind.*$', 'bind 0.0.0.0', use_sudo=True)
    files.append('/etc/redis.conf', 'bind 0.0.0.0', use_sudo=True)
    require.service.restarted('redis')


@task
@roles('database')
def database(name='default', db_version=None):
    import warnings
    from django.conf import settings
    db = settings.DATABASES[name]
    warnings.simplefilter('ignore', DeprecationWarning)

    execute(base)

    # initialize postgres
    require.postgres.server(PG_VERSION)

    pg_service = postgres.service_name(PG_VERSION)
    require.service.started(pg_service)
    require.service.enabled(pg_service)
    require.postgres.listening_on('*')

    # This should be more secure, but it's on the private network currently so ehhhh
    for host in env.roledefs['application']:
        if IP_ADDR.match(host):
            host = "%s/32" % host
        require.postgres.hba_rule('host', db['NAME'], db['USER'], host, 'trust')

    require.postgres.user(db['USER'])
    require.postgres.database(db['NAME'], db['USER'])

    # not relevant to labsite, but for future deployment scripts
    # sudo('psql -c "CREATE EXTENSION postgis" -d %(NAME)s' % db, user='postgres')
    # sudo('psql -c "CREATE EXTENSION postgis_topology" -d %(NAME)s' % db, user='postgres')


@task
def devel():
    """
    Provision a host in preparation for development.
    """
    require.postgres.packages(PG_VERSION)

    require.rpm.repository('epel')
    require.packages([
        'git',
        'gcc',
    ])

    require.python.pip()
    require.python.package('virtualenv', use_sudo=True)
    require.python.virtualenv('venv')

    with python.virtualenv('venv'), cd('labsite'):
        require.python.requirements('requirements.txt', upgrade=True)


@task(default=True)
def all():
    secrets.context('application')
    execute(_all, hosts=role_hosts())


@task
def _all():
    role_tasks = {
        'application': [frontend, worker, ],
        'broker': [broker, ],
        'database': [database, ],
    }

    tasks = []
    for role in host_roles(env.host):
        if role in role_tasks:
            tasks.extend(role_tasks[role])

    pipeline.process(*tasks)
