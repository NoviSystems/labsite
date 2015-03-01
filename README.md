# lab.oscar #

Labsite is a simple project that organizes the internal apps used at OSCAR Lab.


## Overview ##

These instructions exist to help get developers started on development for Oscar Lab's
internal applications. It's unlikely that the labsite project itself will see much
development over time.

### System Structure ###

Labsite has a fairly common and simple structure. It is composed of a web application
and server, and is supported by a message broker and database server. The web application
is built on top of the [Django](http://djangoproject.com) web framework, and uses
[Celery](http://www.celeryproject.org/)) for handling asynchronous task execution. In a
production like environment, the application server would be a gunicorn or uWSGI server
operating behind [nginx](http://nginx.org). In development, the web server would simply
be Django's builtin development server.

The message broker is used for routing tasks to the Celery worker processes. These
workers operate in the background and are largely independently of the web app. Labsite
uses [redis](http://redis.io/) primarily due to its ease of use and configuration.

The database is used for persisting data. [PostgreSQL](http://www.postgresql.org/) is
our database of choice.

If you're unfamiliar with any of those projects or there purposes, don't worry too much -
most of your development work will be with the Django framework. It's only important now
to ensure that they're setup properly, and you'll learn more about them as they become
relevant to your development work.

#### Host Roles ####
Labsite is built around the concept of host roles. A role provides a service that is
used in the overall system. Labsite has three host roles:

- application: Provides the web application, worker processes, and web server.
- broker: Provides the message broker service.
- database: Provides the database server.

A host may be assigned one or more of these roles. In our production environments, a host
usually only provides a single role. When developing labsite, you'll either hook into 
existing hosts that provide these service, or you'll set them up in an automated fashion
with vagrant and fabric.


## Getting Started ##

This guide assumes some prior familiarization with [Bash](ss64.com/bash/), 
[Git](http://git-scm.com/), [virtualenv](http://www.virtualenv.org/en/latest/),
[Vagrant](https://vagrantup.com), and [Fabric](http://www.fabfile.org).

Before doing anything, ensure that you have a github account and that you've setup
your SSH keys.

Next, you need to decide on your development workflow. There are two main stragies: 

- local development
- remote development

The names are self-explanatory, however their workflows are somewhat different. 

#### local development overview ####
This workflow leverages your local system. Because the software installation process is
fairly involved and requires a lot of additional software packages, a Vagrantfile has
been provided that describes a production-like environment. Using vagrant will allow you
to isolate the installed software to the virtual machines, allowing you to easily tear
them down and reinitialize them. 

The primary advantage with using vagrant is that it enables you to use our provisioning
and deployment scripts. They are an automated way of installing all of the necessary
software. The downside is that vagrant will eat some of your system resources. There are
also some potential issues when working on Windows. 

[Local development workflow](#local-development)

This workflow is recommended for when you have a fairly capable machine running Linux or
OS X. 

#### remote development overview ####
This workflow leverages resources located within OSCAR Lab's internal network. The
advantage here is that all software and services are installed on OSCAR Lab's develpment machines. While the service will already be setup/installed, they will however require
configuring. Additionally, you may experience connection issues when operating outside
of NCSU's network. This is not always the case, but some public networks exhibit poor
performance when attempting to SSH into the lab.

[Remote development workflow](#remote-development)

### Local development ###
To get started, you'll need to clone the repository. It contains the Vagrantfile that
enables the local development workflow as well as the scripts for provisioning the VMs
and deploying the software.

    $ cd <your/working/directory>
    $ git clone git@github.com:ITNG/labsite

With the repository downloaded, we'll setup a virtual enviroment and install the python
packages used by the deployment scripts.

    $ cd labsite
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -Ur deploy-requirements.txt

Additionally, go ahead and boot the Vagrant VMs. If this is your first time booting the
VMs, it may be slow as it has to download the vagrant boxes/images.

    # vagrant up

The Vagrantfile describes two hosts - ``application`` and ``services``. The application
VM has been setup to run both a production like server, as well as allow you to develop
and run the management server. The services VM is where the broker and database will be
installed. 

It's important to note that the current directory is synced to the home directory on the
application VM. Any changes to this directory will also have effect in the application
VM. 

If you're developing any of the labsite apps, you should go ahead and follow the
instructions posted in their respective readme files. 

- [worklog](github.com/ITNG/worklog)
- [foodapp](github.com/ITNG/foodapp)

After installing the software, you'll need to configure labsite's django settings. Copy
the example secrets and settings and customize them to fit your needs. At minimum, the
postgres settings will need to be updated. Make sure that you also set the SECRET_KEY
value, which can be located in secrets.py. It may also be overridden in the settings.

    $ cp labsite/secrets.ex.py labsite/secrets.py
    $ cp labsite/settings.ex.py labsite/settings.py

With our requirements installed, the vagrant machines booted, and labsite configured,
we're ready to provision the Vagrant machines. This may take a little while, so grab a
cup of coffee or something.

    $ fab provision.all

At this point, postgres and redis are installed and running on the services VM. They have also been configured to accept connections from the application host. The application
host has most of the software installed, and is ready to be deployed to for production
level testing. It also has this directory synced to the vagrant user's home directory,
which will allow us to run the django development server.

To finish setting up the development environment:

    $ fab vagrant.on:local provision.devel

Once provisioned, SSH into `application` and finish installing the python packages. Note
that the existing `.env` virtualenv will not work within the `application` VM, as the symlinks will break (discussing this is outside the scope of this tutorial).  Instead, a
`venv` has been created in the vagrant home directory.

    $ vagrant ssh application
    $ source venv/bin/activate

    $ cd labsite
    $ pip install -Ur requirements.txt

Additionally, if you are developing an app, you will need to install it's requirements.
If you are not developing that app, you will need to install the app to the virtualenv.

Using worklog as an example, to install the requirements:

    $ pip install -Ur path/to/worklog/requirements.txt
    # probably something like:
    $ pip install -Ur .app/worklog/requirements.txt

To install the app:

    $ pip install git+git://github.com/ITNG/worklog.git

Now, migrate the database

    $ python manage.py syncdb
    $ python manage.py migrate --all

Finally, you can run the development server:

    $ python manage.py runserver 0.0.0.0:8000

You may also need to run the celery worker to execute asynchronous tasks:

    $ python manage.py celeryd

The application VM has a static IP of `192.168.10.20`. You should be able to reach the
development server at http://192.168.10.20:8000.


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

Labsite also operates on the notion of server environments. An environment a
configuration that describes how to properly connect and communicate with the hosts in
a specific deployment. For example, the 'stag' environment contains the variables
necessary for connecting to OSCAR's staging environment. These configurations live in
`environ.json`. If no environ is specified, it defaults to 'default'.

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

To deploy to a specific environment such as staging:

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

    If lunchapp is serving an Internal Server Error, ensure that there is an 
    instance of a RiceCooker in the database. Login to the admin pages as a
    superuser and create a RiceCooker. Refresh the page.
