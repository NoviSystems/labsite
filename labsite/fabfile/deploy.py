
from fabric.api import task, runs_once, execute
from fabric.api import settings, env, hide, cd
from fabric.api import local, run
from fabtools import require
from fabtools import service
from fabtools import supervisor
from fabtools import python
from fabtools import files
from fabtools import user


@task
def log_predeploy():
    details = {
        'local': local('whoami', quiet=True),
        'user': run('whoami', quiet=True),
        'date': run('$(date)', quiet=True),
    }

    with user.masquerade('labuser'):
        files.append('log/deployment.log', '%(date)s %(local)s/%(user)s' % details, use_sudo=True)

        if files.is_dir('labsite'):
            with cd('labsite'):
                files.append('log/deployment.log', 'pre-deploy: %(branch)s/%(commit)s' % {
                    'branch': run('$(git symbolic-ref --short HEAD)', quite=True),
                    'commit': run('$(git rev-parse HEAD)', quiet=True),
                }, use_sudo=True)


@task
def log_postdeploy():

    with user.masquerade('labuser'):
        with cd('labsite'), settings(hide('warnings'), warn_only=True):
            details = {
                'branch': run('$(git symbolic-ref --short HEAD)', quite=True),
                'commit': run('$(git rev-parse HEAD)', quiet=True),
            }
        files.append('log/deployment.log', 'post-deploy: %(branch)s/%(commit)s' % details, use_sudo=True)
        files.append('log/deployment.log', 'success\n', use_sudo=True)


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
            for version in range(depth)[::-1]:
                if files.is_dir(str(version)):
                    files.move(str(version), str(version + 1))

                if files.is_file('requirements.%d.txt' % version):
                    files.move(
                        'requirements.%d.txt' % version,
                        'requirements.%d.txt' % version + 1,
                    )

        if files.is_dir('labsite'):
            files.copy('labsite', 'backups/0', recursive=True)

        if files.is_dir('venv'):
            with python.virtualenv('venv'):
                run("pip freeze > requirements.0.txt")


@task
@user.masquerade('labuser')
def rollback(depth=9):
    """
    Rollback the existing project code to the latest backup.
    """
    with cd(user.home_directory('labuser')):
        files.move('backups/0', 'labsite')
        with python.virtualenv('venv'):
            require.python.requirements('backups/requirements.0.txt')

        with cd('backups'):
            for version in range(depth):
                if files.is_dir(str(version + 1)):
                    files.move(str(version + 1), str(version))

                if files.is_file('requirements.%d.txt' % version + 1):
                    files.move(
                        'requirements.%d.txt' % version + 1,
                        'requirements.%d.txt' % version,
                    )


@task
@user.masquerade('labuser')
def application(branch, **kwargs):
    execute(backup)

    require.git.working_copy('git@github.com:ITNG/labsite.git', branch=branch)

    require.python.virtualenv('venv')
    with python.virtualenv('venv'):
        kwargs.setdefault('foodapp', 'master')
        kwargs.setdefault('worklog', 'master')

        require.python.packages([
            'git+git://github.com/ITNG/foodapp.git@$%(foodapp)s' % kwargs,
            'git+git://github.com/ITNG/worklog.git@$%(worklog)s' % kwargs,
        ], upgrade=True)

        with cd('labsite'):
            require.python.requirements('requirements.txt', upgrade=True)
            require.python.requirements('labsite/setup/requirements.txt', upgrade=True)

            files.copy('labsite/settings_%s.py' % env.environ, 'labsite/settings.py')
            files.copy('~/secrets.py', 'labsite/secrets.py')

            run('python manage.py collectstatic --noinput')
            # run('python manage.py compress --force')

            config = {
                'HOME': run('echo ~', quiet=True),
            }

            with user.unmasque():
                files.template_file(
                    '/etc/nginx/conf.d/labsite.conf',
                    template_source='labsite/nginx.conf',
                    # template_source='%s/labsite/nginx.conf' % user.home_directory('labsite'),
                    template_contexnts=config,
                    use_sudo=True
                )
                files.template_file(
                    '/etc/supervisord.d/labsite.ini',
                    template_source='labsite/supervisor.ini',
                    # template_source='%s/labsite/supervisor.ini' % user.home_directory('labsite'),
                    template_contexnts=config,
                    use_sudo=True
                )

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
def process():
    # execute(backup)
    execute(log_predeploy)
    execute(application)
    execute(database)
    execute(log_postdeploy)
