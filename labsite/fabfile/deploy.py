
from fabric.api import task, cd, env, run
from fabtools import require
from fabtools import service
from fabtools import supervisor
from fabtools import python
from fabtools import files
from fabtools import user


def log_deployment():
    iam = run('whoami')
    (iam)


@task
@user.masquerade('labuser')
def backup(depth=9):
    """
    Backup the existing project code with an additional ``depth`` number of backups.

    The most recent backup is copied to ~/backups/0 with older versions incrementing
    the directory number.
    """
    with cd(user.home_directory('labuser')):
        with cd('backups'):
            for version in range(depth)[::-1]:
                if files.is_dir(str(version)):
                    files.move(str(version), str(version + 1))

                if files.is_file('requirements.%d.txt' % version):
                    files.move(
                        'requirements.%d.txt' % version,
                        'requirements.%d.txt' % version + 1,
                    )

        files.copy('labsite', 'backups/0', recursive=True)
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
def application(branch, app_branches=None):
    require.git.working_copy('git@github.com:ITNG/labsite.git', branch=branch)

    require.python.virtualenv('venv')
    with python.virtualenv('venv'):
        app_branches.setdefault('foodapp', 'master')
        app_branches.setdefault('worklog', 'master')

        require.python.packages([
            'git+git://github.com/ITNG/foodapp.git@$%(foodapp)s' % app_branches,
            'git+git://github.com/ITNG/worklog.git@$%(worklog)s' % app_branches,
        ], upgrade=True)

        with cd('labsite'):
            require.python.requirements('requirements.txt', upgrade=True)
            require.python.requirements('labsite/setup/requirements.txt', upgrade=True)

            files.copy('labsite/settings_%s.py' % env.environ, 'labsite/settings.py')
            files.copy('~/secrets.py', 'labsite/secrets.py')

            run('python manage.py collectstatic --noinput')
            # # python $PROJECT_DIR/manage.py compress --force

            run('python manage.py syncdb --noinput')
            run('python manage.py migrate --all --noinput --no-initial-data')

        supervisor.update_config()
        supervisor.restart_process('all')
        service.restart('nginx')
