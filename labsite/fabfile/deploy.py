
from fabric.api import task, runs_once, execute
from fabric.api import settings, env, hide, cd, path
from fabric.api import local, run, sudo
from fabric.contrib.files import append, upload_template
from fabtools import require
from fabtools import service
from fabtools import supervisor
from fabtools import python
from fabtools import files
from fabtools import user

from importlib import import_module
from inspect import getsourcefile
import posixpath

from labsite.fabfile import PG_VERSION


__all__ = (
    'backup', 'rollback', 'application', 'database', 'process',
)


@task
def pre_log():
    with settings(hide('running')):
        # these details need to be retrieved before masquerading as labuser
        details = {
            'local': local('whoami', capture=True),
            'user': run('whoami', quiet=True),
            'date': run('$(date)', quiet=True),
        }

        with user.masquerade('labuser'):
            append('log/deployment.log', '%(date)s %(local)s/%(user)s' % details)

            if files.is_dir('labsite/.git'):
                append('log/deployment.log', 'pre-deploy: %(branch)s/%(commit)s' % {
                    'branch': run('git --git-dir labsite/.git symbolic-ref --short HEAD', quiet=True),
                    'commit': run('git --git-dir labsite/.git  rev-parse HEAD', quiet=True),
                })


@task
def post_log():
    with settings(hide('running')), \
         user.masquerade('labuser'):

        details = {
            'branch': run('git --git-dir labsite/.git symbolic-ref --short HEAD', quiet=True),
            'commit': run('git --git-dir labsite/.git rev-parse HEAD', quiet=True),
        }
        append('log/deployment.log', 'post-deploy: %(branch)s/%(commit)s' % details)
        append('log/deployment.log', 'success\n')


@task
@runs_once
@user.masquerade('labuser')
def backup(depth=9):
    """
    Backup the existing project code with an additional ``depth`` number of backups.

    The most recent backup is copied to ~/backups/0 with older versions incrementing
    the directory number.
    """
    with cd(user.home_directory('labuser')):
        if not files.is_dir('labsite'):
            return

        with cd('backups'):
            if files.is_dir(str(depth)):
                run('rm -rf %s' % depth)

            for version in range(depth)[::-1]:
                if files.is_dir(str(version)):
                    files.move(str(version), str(version + 1))

                if files.is_file('requirements.%d.txt' % version):
                    files.move(
                        'requirements.%d.txt' % version,
                        'requirements.%d.txt' % (version + 1),
                    )

        if files.is_dir('labsite'):
            files.copy('labsite', 'backups/0', recursive=True)

        if files.is_dir('venv'):
            with python.virtualenv('venv'):
                run("pip freeze > backups/requirements.0.txt")


@task
@user.masquerade('labuser')
def rollback(depth=9):
    """
    Rollback the existing project code to the latest backup.
    """
    with cd(user.home_directory('labuser')):
        run('rm -rf labsite')
        files.move('backups/0', 'labsite')
        with python.virtualenv('venv'):
            if files.is_file('backups/requirements.0.txt'):
                require.python.requirements('backups/requirements.0.txt')

        with cd('backups'):
            for version in range(depth):
                if files.is_dir(str(version + 1)):
                    files.move(str(version + 1), str(version))

                if files.is_file('requirements.%d.txt' % (version + 1)):
                    files.move(
                        'requirements.%d.txt' % (version + 1),
                        'requirements.%d.txt' % version,
                    )


@task
@user.masquerade('labuser')
def application(branch='master', **kwargs):

    with settings(prompts={'Are you sure you want to continue connecting (yes/no)? ': 'yes'}):
        require.git.working_copy('git@github.com:ITNG/labsite.git', branch=branch)

    require.python.virtualenv('venv')
    with python.virtualenv('venv'):
        kwargs.setdefault('foodapp', 'master')
        kwargs.setdefault('worklog', 'master')

        require.python.packages([
            'git+git://github.com/ITNG/foodapp.git@%(foodapp)s' % kwargs,
            'git+git://github.com/ITNG/worklog.git@%(worklog)s' % kwargs,
        ], upgrade=True)

        with cd('labsite'):
            require.python.requirements('requirements.txt', upgrade=True)
            with path('/usr/pgsql-%s/bin' % PG_VERSION):
                require.python.requirements('labsite/setup/requirements.txt', upgrade=True)

            if env.upload_settings:
                settings_module = import_module(env.django_settings)
                upload_template(getsourcefile(settings_module), 'labsite/settings.py', {})
            else:
                files.copy('labsite/settings_%s.py' % env.environ, 'labsite/settings.py')
            files.copy('%s/secrets.py' % user.home_directory('labuser'), 'labsite/secrets.py')

            run('python manage.py collectstatic --noinput')
            # run('python manage.py compress --force')

    # deploy the webserver/proxy configurations
    with user.unmasque():
        config = {'USERNAME': 'labuser'}
        config['HOME_DIR'] = user.home_directory('labuser')
        config['PROJ_DIR'] = posixpath.join(config['HOME_DIR'], 'labsite')

        require.files.template_file(
            '/etc/nginx/conf.d/labsite.conf',
            sudo('cat %(PROJ_DIR)s/labsite/setup/nginx.conf' % config, quiet=True),
            context=config,
            use_sudo=True
        )
        require.files.template_file(
            '/etc/supervisord.d/labsite.ini',
            sudo('cat %(PROJ_DIR)s/labsite/setup/supervisord.ini' % config, quiet=True),
            context=config,
            use_sudo=True
        )

        # ensure that the services are started
        require.service.started('supervisord')
        require.service.started('nginx')

        # and that their configurations/processes are reloaded
        supervisor.update_config()
        supervisor.restart_process('all')
        service.restart('nginx')


@task
@user.masquerade('labuser')
def database():
    require.python.virtualenv('venv')
    with python.virtualenv('venv'), cd('labsite'):
        run('python manage.py syncdb --noinput')
        run('python manage.py migrate --all --noinput --no-initial-data')


@task(default=True)
def process(*args, **kwargs):
    execute(pre_log, roles=['application'])
    execute(backup, roles=['application'])
    execute(application, roles=['application'], *args, **kwargs)
    execute(database, roles=['application'])
    execute(post_log, roles=['application'])
