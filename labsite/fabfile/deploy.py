
from fabric.api import task, runs_once
from fabric.api import settings, env, hide, cd
from fabric.api import local, run, sudo
from fabric.contrib.files import append, upload_template
from fabtools import require
from fabtools import supervisor
from fabtools import python
from fabtools import files
from fabtools import user
from prefab import pipeline

from importlib import import_module
from inspect import getsourcefile
import posixpath


__all__ = (
    'backup', 'rollback', 'application', 'database', 'process',
)


@task
@pipeline.once
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
@pipeline.once
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
@pipeline.once
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
@pipeline.once
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
@pipeline.once
@pipeline.requires(backup)
@user.masquerade('labuser')
def application(labsite=None, foodapp=None, worklog=None):
    """
    Deploys the application code.
    """
    branches = env.git_branches

    # set branch defaults and local overrides
    for repo in ['labsite', 'foodapp', 'worklog']:
        branches.setdefault(repo, 'master')

        if locals()[repo] is not None:
            branches[repo] = locals()[repo]

    # clone labsite repo
    with settings(prompts={'Are you sure you want to continue connecting (yes/no)? ': 'yes'}):
        require.git.working_copy('git@github.com:ITNG/labsite.git', branch=branches['labsite'])

    # install packages
    require.python.virtualenv('venv')
    with python.virtualenv('venv'):

        require.python.packages([
            'git+git://github.com/ITNG/foodapp.git@%(foodapp)s' % branches,
            'git+git://github.com/ITNG/worklog.git@%(worklog)s' % branches,
        ], upgrade=True)

        require.python.requirements('labsite/requirements.txt', upgrade=True)

    # move files, run commands
    with python.virtualenv('venv'), cd('labsite'):

        if env.upload_settings:
            settings_module = import_module(env.django_settings)
            upload_template(getsourcefile(settings_module), 'labsite/settings.py', {})
        else:
            files.copy('labsite/settings_%s.py' % env.environ, 'labsite/settings.py')
        files.copy('%s/secrets.py' % user.home_directory('labuser'), 'labsite/secrets.py')

        run('python manage.py collectstatic --noinput')
        # run('python manage.py compress --force')


@task
@pipeline.once
@pipeline.requires(application)
def frontend():
    config = {'USERNAME': 'labuser'}
    config['HOME_DIR'] = user.home_directory('labuser')
    config['PROJ_DIR'] = posixpath.join(config['HOME_DIR'], 'labsite')

    # supervisor ini
    require.supervisor.process_template(
        'gunicorn',
        sudo('cat %(PROJ_DIR)s/labsite/setup/gunicorn.ini' % config, quiet=True),
        context=config,
        use_sudo=True,
    )

    require.service.started('supervisord')
    require.service.enabled('supervisord')
    supervisor.update_config()
    supervisor.restart_process('all')

    require.files.template_file(
        '/etc/nginx/conf.d/labsite.conf',
        sudo('cat %(PROJ_DIR)s/labsite/setup/nginx.conf' % config, quiet=True),
        context=config,
        use_sudo=True,
    )

    require.service.started('nginx')
    require.service.enabled('nginx')
    require.service.restarted('nginx')


@task
@pipeline.once
@pipeline.requires(application)
def worker():
    config = {'USERNAME': 'labuser'}
    config['HOME_DIR'] = user.home_directory('labuser')
    config['PROJ_DIR'] = posixpath.join(config['HOME_DIR'], 'labsite')

    # supervisor ini's
    require.supervisor.process_template(
        'celery-beat',
        sudo('cat %(PROJ_DIR)s/labsite/setup/celery-beat.ini' % config, quiet=True),
        context=config,
        use_sudo=True,
    )
    require.supervisor.process_template(
        'celery-worker',
        sudo('cat %(PROJ_DIR)s/labsite/setup/celery-worker.ini' % config, quiet=True),
        context=config,
        use_sudo=True,
    )

    require.service.started('supervisord')
    require.service.enabled('supervisord')
    supervisor.update_config()
    supervisor.restart_process('all')


@task
@runs_once
@pipeline.requires(application)
@user.masquerade('labuser')
def database():
    require.python.virtualenv('venv')
    with python.virtualenv('venv'), cd('labsite'):
        run('python manage.py syncdb --noinput')
        run('python manage.py migrate --all --noinput --no-initial-data')


@task(default=True)
def process(labsite='master', foodapp='master', worklog='master'):
    env.roles = ['application']
    env.git_branches = {
        'labsite': labsite,
        'foodapp': foodapp,
        'worklog': worklog,
    }

    pipeline.process(
        pre_log,
        backup,
        frontend,
        worker,
        database,
        post_log,
    )
