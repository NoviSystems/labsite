
from fabric.api import task, roles, env, execute, sudo
from fabric.contrib.files import sed
from fabtools import require
from fabtools import user
import fabtools

from labsite.fabfile import config
from labsite.fabfile import PG_VERSION


__all__ = [
    'application', 'broker', 'database', 'all',
]


@task
def base():
    fabtools.ssh.harden()
    fabtools.systemd.restart('sshd')

    # selinux - reference:
    # http://wiki.centos.org/HowTos/SELinux
    sudo('setenforce 1')
    sed('/etc/selinux/config', r'^SELINUX=.*$', 'SELINUX=enforcing', use_sudo=True)

    # setup hostname?
    # http://ask.xmodulo.com/change-hostname-centos-rhel-7.html
    # http://www.rackspace.com/knowledge_center/article/centos-hostname-change
    sudo('hostnamectl set-hostname %(host)s' % env)

    require.package('ntp')
    require.service.enabled('ntpd')
    require.service.stopped('ntpd')
    sudo('ntpdate pool.ntp.org')
    require.service.started('ntpd')

    require.package('firewalld')
    require.service.started('firewalld')
    require.service.enabled('firewalld')


@task
@roles('application')
def application():
    secrets_context = config.secrets_context()

    execute(base)

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
    execute(config.certify)
    sudo('setsebool -P httpd_read_user_content 1')

    sudo('firewall-cmd --add-port=80/tcp')
    sudo('firewall-cmd --add-port=80/tcp --permanent')
    sudo('firewall-cmd --add-port=443/tcp')
    sudo('firewall-cmd --add-port=443/tcp --permanent')
    require.python.pip()
    require.python.package('virtualenv', use_sudo=True)

    with user.masquerade('labuser'):
        require.directory('log')
        require.file('log/celeryd.log')
        require.file('log/celerybeat.log')
        require.file('log/deployment.log')

        require.directory('backups')

        require.python.virtualenv('venv')

        execute(config.application_secrets, **secrets_context)


@task
@roles('broker')
def broker():
    execute(base)

    require.rpm.repository('epel')
    require.package('redis')

    sudo('firewall-cmd --add-port=6379/tcp')
    sudo('firewall-cmd --add-port=6379/tcp --permanent')


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

    pg_service = require.postgres._service_name(PG_VERSION)
    require.service.started(pg_service)
    require.service.enabled(pg_service)
    require.postgres.listening_on('*')

    # This should be more secure, but it's on the private network currently so ehhhh
    for host in env.roledefs['application']:
        require.postgres.hba_rule('host', db['NAME'], db['USER'], "%s/32" % host, 'trust')

    sudo('firewall-cmd --add-port=5432/tcp')
    sudo('firewall-cmd --add-port=5432/tcp --permanent')

    require.postgres.user(db['USER'])
    require.postgres.database(db['NAME'], db['USER'])

    # not relevant to labsite, but for future deployment scripts
    # sudo('psql -c "CREATE EXTENSION postgis" -d %(NAME)s' % db, user='postgres')
    # sudo('psql -c "CREATE EXTENSION postgis_topology" -d %(NAME)s' % db, user='postgres')


@task(default=True)
def all():
    execute(application)
    execute(broker)
    execute(database)
