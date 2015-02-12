# lab.oscar #

Labsite is a simple project that organizes the internal apps used at OSCAR Lab.


## Overview ##

These instructions exist to help get developers started on development for Oscar Lab's
internal applications. It's unlikely that the labsite project itself will see much
development over time.

### Organization ###

Labsite is composed of three primary services:
- the application server (running [Django](http://djangoproject.com) &
[Celery](http://www.celeryproject.org/))
- the message broker ([redis](http://redis.io/))
- and the database ([PostgreSQL](http://www.postgresql.org/))

The deployment scripts and server setup assume that there are host roles that provide
these services. That is specifically, that there are the ``application``, ``broker``,
and ``database`` roles that a host may be assigned.

## Getting Started ##

This guide assumes some prior familiarization with [Bash](ss64.com/bash/), 
[Vagrant](https://vagrantup.com), [Fabric](http://www.fabfile.org), and
[virtualenv](http://www.virtualenv.org/en/latest/).

The roles described in the project's organization are the basis of the Vagrantfile and
fabfile's structure. The Vagrantfile provides a production-like environment with three
VMs that provide the above roles. This environment is useful for testing your changes
before deploying them to staging and production. The fabfile is structured to provision
and deploy to the three host roles. 

Development should be performed locally with vagrant, or remotely on the development
server. It is not recommended that you develop locally without vagrant, as installing
and running the various services correctly (postgres, redis) can be problematic.


### Local development ###
To get started, you'll need to clone the repository and install the deploy requirements
inside a virtual environment.

    $ git clone git@github.com:ITNG/labsite
    $ cd labsite
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -Ur requirements-deploy.txt

If you're developing any of the labsite apps, follow the instructions posted in their
respective repos. 

After installing the software, you'll need to configure labsite's django settings. Copy
the example secrets and settings and customize them to fit your needs. At minimum, the
postgres settings will need to be updated. Make sure that you set the SECRET_KEY value.

    $ cp labsite/secrets.ex.py labsite/secrets.py
    $ cp labsite/settings.ex.py labsite/settings.py

With labsite configured, we need to setup the Vagrant development environment. These VMs
will provide the database and broker services in addition to an application server.
Simply boot the VMs and run the provisioning scripts.

    $ vagrant up
    $ fab provision.all

These roles can also be referred to by name and individual provisioned. For example:

    $ vagrant up database
    $ fab provision.database

The development environment can now be deployed to in order to test changes. However,
committing and deploying each set of changes is not an efficient development workflow.
You should only really deploy to the dev environment before attempting to deploy to
staging and production.

#### The local VM ####
To enable easier local development, a fourth `local` Vagrant VM is defined. It syncs
this project directory to the vagrant user's home directory, and is structured to
manually run Django's development server.

To develop locally, you will need to provision the `local` VM. This VM syncs your project
folder to the vagrant user's home directory on `local`. Provisioning will allow you to
install the necessary dependencies for the project.

    $ vagrant up local
    $ fab vagrant.on:local provision.local

Once provisioned, SSH into `local` and setup the software. Note that the existing `.env`
virtualenv will not work within the `local` VM, as the symlinks will break. Instead, a
`venv` exists in the vagrant home directory.

    $ vagrant ssh local
    $ source venv/bin/activate

    $ cd labsite
    $ pip install -Ur requirements.txt

Additionally, you will need to install the apps manually to the virtualenv. If you are
developing an app, you would need to install the app's requirements. For example:

    $ pip install git+git://github.com/ITNG/foodapp.git
    $ pip install -Ur path/to/worklog/requirements.txt

Finally, migrate the database

    $ python manage.py syncdb
    $ python manage.py migrate --all

To run the development server, use the manage.py runserver command:

    $ python manage.py runserver 0.0.0.0:8000

You may also need to run the celery worker to execute asynchronous tasks:

    $ python manage.py celeryd

The `local` VM has an assigned IP Address of `192.168.10.2`.


### Remote development ###
To develop remotely, SSH into the development server, clone the repository, and install
the project requirements.

    $ git clone git@github.com:ITNG/labsite
    $ cd labsite
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -Ur requirements-deploy.txt

If you're developing any of the labsite apps, follow the instructions posted in their
respective repos. Otherwise, pip install the apps. Do not pip install the app while
developing locally, as files may conflict.

    $ pip install git+git://github.com/ITNG/foodapp.git
    $ pip install git+git://github.com/ITNG/worklog.git

After installing the software, you'll need to configure labsite's django settings. Copy
the example secrets and settings and customize them to fit your needs. At minimum, the
postgres settings and broker URL will need to be updated.

    $ cp labsite/secrets.ex.py labsite/secrets.py
    $ cp labsite/settings.ex.py labsite/settings.py

You will also need to ensure that the database and broker are setup to allow your
incoming connection requests. For postgres, this will require creating a user and a
database and setting up the rules that allow access from the development server. On the
postgres server:

    $ sudo -iu postgres
    $ createuser <username> --no-superuser --no-createdb --no-createrole
    $ createdb <username>_lab -O <username>

Add a rule like the following to the pg_hba.conf:

    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    ...
    host    <username>_lab  <username>      dev.oscar.priv          peer

With labsite setup, you should verify that your development environment can access the
services.

    # To test your postgres connection:
    $ python manage.py dbshell

    # To test your broker connection:
    $ python manage.py celeryd status
    (verify that this works)


### Development Database ###
For development, you can either manually populate from an empty database, or make a copy
of a production database and import it into your development database.


## Deployment ##

Deployment *does not* copy your working tree to a server. Deployment will update a
server's installation to a particular revision in git. By default the server is updated
to master, but you can deploy a server to a different branch. Additionally, you can
specify which branch to deploy for the labsite apps.

### How to Deploy ###

Before deploying, make sure you've committed your latest changes. You will also need to
ensure the following:
- You will need sudo access on the target machine.
- You will need to have an SSH agent enabled that supports agent forwarding.
- Your SSH keys need to be associated with your GitHub user.
- Your GitHub user will need to have to this repo.

Before deploying to staging or production, attempt to depoy to the test environment.

    $ fab deploy

To deploy a specific labsite branch:

    $ fab deploy:<branch name>

You can also deploy specific app branches:

    $ fab deploy:worklog=<some other branch>

To deploy to production or staging:

    $ fab environ:stag deploy
    or
    $ fab deploy --set environ=stag


## Troubleshooting ##

502 Bad Gateway:

    If a 502 is encountered, ensure that the IP address and port number defined
    in the nginx configuration file match the IP address and port number defined for
    gunicorn in the supervisord configuration file.

500 Internal Server Error:

    As of Django 1.5, the default for the ALLOWED_HOSTS field in Settings.py is now
    "[]".  As a result, if the field is left blank or none of the strings within the
    list match the Host header, Django will automatically serve a 500 error.
    To fix this issue, insert the appropriate URLs into the list of allowed hosts. 

