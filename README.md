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

If you're unfamiliar with any of those projects or there purposes, don't worry too much -
most of your development work will be with the Django framework. It's only important now
to ensure that they're setup properly, and you'll learn more about them as they become
relevant to your development work.

#### Host Roles ####
Labsite is built around the concept of host roles. A role provides a service that is
used within system. Labsite has three host roles:

- application: Provides the web application, worker processes, and web server.
- broker: Provides the message broker service.
- database: Provides the database server.

A host may be assigned one or more of these roles. In our production environments, a host
usually only provides a single role. When developing labsite, you'll either hook into 
existing hosts that provide these service, or you'll set them up on your local machine in
an automated fashion with vagrant and fabric.


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
advantage here is that all software and services are installed on OSCAR Lab's develpment
machines. While the service will already be setup/installed, they will however require
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
packages used by the deployment scripts. NOTE: For Windows users, the activate script
is in .env/Scripts/activate

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

- [worklog](https://github.com/ITNG/worklog)
- [foodapp](https://github.com/ITNG/foodapp)

After installing the software, you'll need to configure labsite's django settings. Copy
the example secrets and settings and customize them to fit your needs. At minimum, the
postgres settings will need to be updated. Make sure that you also set the SECRET_KEY
value, which can be located in secrets.py. It may also be overridden in the settings.

    $ cp labsite/secrets.ex.py labsite/secrets.py
    $ cp labsite/settings.ex.py labsite/settings.py
    
Make sure that both files have been set up properly, otherwise the following step may fail.

With our requirements installed, the vagrant machines booted, and labsite configured,
we're ready to provision the Vagrant machines. This may take a little while, so grab a
cup of coffee or something. Note that the provisioning process will ask you for some
settings values up front. For now, you can skip those questions.

    $ fab provision.all

At this point, postgres and redis are installed and running on the services VM. They have
also been configured to accept connections from the application host. The application
host has most of the software installed, and is ready to be deployed to for production
level testing. It also has this directory synced to the vagrant user's home directory,
which will allow us to run the django development server.

To finish setting up the development environment:

    $ fab vagrant.on:application provision.devel

Once provisioned, SSH into `application` and finish installing the python packages. Note
that the existing `.env` virtualenv will not work within the `application` VM, as the
symlinks will break (discussing this is outside the scope of this tutorial).  Instead, a
`venv` has been created in the vagrant home directory.

    $ vagrant ssh application
    $ source venv/bin/activate

    $ cd labsite
    $ pip install -Ur requirements.txt

Additionally, if you are developing one of the labsite apps, you will need to follow its
setup instructions and install it's requirements. If you are not developing that app, you
will need to install the app to the virtualenv. You do *not* want to both setup the
project and install it to your environment, as you may get file conflicts.

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

If you're unable to reach the development server from your browser, you probably need to
open the port to allow incoming connections.

    $ sudo firewall-cmd --add-port=8000/tcp --permanent
    $ sudo firewall-cmd --add-port=8000/tcp

You may also need to run the celery worker to execute asynchronous tasks:

    $ python manage.py celeryd

The application VM has a static IP of `192.168.10.20`. You should be able to reach the
development server at http://192.168.10.20:8000.


### Remote development ###
To develop remotely on OSCAR Lab's infrastructure, you'll need to install the software
on the development server, then configure the database and broker servers to accept
connections from the dev server. 


#### Installing software ####
First, SSH into the the dev server, clone the repository, and install the project
requirements into a virtualenv.

    $ git clone git@github.com:ITNG/labsite
    $ cd labsite
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -Ur requirements.txt

Additionally, if you are developing one of the labsite apps, you will need to follow its
setup instructions and install it's requirements. If you are not developing that app, you
will need to install the app to the virtualenv. You do *not* want to both setup the
project and install it to your environment, as you may get file conflicts.

- [worklog](github.com/ITNG/worklog)
- [foodapp](github.com/ITNG/foodapp)

Using worklog as an example, to install the requirements:

    $ pip install -Ur path/to/worklog/requirements.txt
    # probably something like:
    $ pip install -Ur .app/worklog/requirements.txt

To install the app:

    $ pip install git+git://github.com/ITNG/worklog.git

After installing the software, you'll need to configure labsite's django settings. Copy
the example secrets and settings and customize them to fit your needs. At minimum, the
postgres settings and broker URL will need to be updated. Make sure that you also set the
SECRET_KEY value, which can be located in secrets.py. It may also be overridden in the
settings.

    $ cp labsite/secrets.ex.py labsite/secrets.py
    $ cp labsite/settings.ex.py labsite/settings.py
    
If you need to work on a labsite app which has previously been installed using pip, be sure
to uninstall it and use the setup instructions in the app's readme. Otherwise, labsite may
use the installed version of the app rather than the one you are making changes to.

    $ pip uninstall [appname]


#### Configuring the postgres database ####

Before setting up postgres, you need to be aware of a few details:

- The 'postgres server' is a software service running on an actual server/host.
- There is a postgres system user that is useful to use when configuring postgres. Simply
`sudo -iu postgres` to open a shell as the postgres user.
- Postgres has database users (also known as roles). These roles are not directly related
to system users.
- The postgres server has multiple databases within it. Each database is owned by a user.
- Database access is controlled in the pg_hba.conf file. Each record specifies a
connection type, a client address (IP address, range, or hostname), a database name, a
user name, and the authentication method. The first matching record is used to determine
access and perform authentication.

At minimum, you will need to manually create a user and database. You may also need to
configure the pg_hba.conf file. It is convention at the lab to use your system username
as your database username. It also common to use <username>_<project name> as the name
for your database.

SSH into the posgres server and run the following, replacing <username> with your actual
username:

    $ sudo -iu postgres
    $ createuser <username>
    $ createdb <username>_lab -O <username>

You can now test connecting to your database from the dev server. On dev:

    $ psql -d <username>_lab -h <pg hostname>

###### Troubleshooting connection issues ######

If you're having trouble connecting to your database, there are a few places to start
troubleshooting. 

- check that the postgres service is running
- check the firewall
- check the postgres settings

*check the postgres service*
    
    $ sudo systemctl status postgresql

*check the firewall*

Postgres runs on port 5432. Make sure that the firewall is accepting connections on that
port.

    $ sudo firewall-cmd --query-port=5432/tcp

*check the postgres settings*

Postgres by default only listens to connections on the localhost. Ensure that it is also
listening on its IP address.

    $ sudo -iu postgres
    $ cd data 
    # or
    $ cd <version>/data
    $ cat postgresql.conf

The `listen_addresses` value should have a string value of '*' or its IP address.

Check the pg_hba.conf file. This is a very common source of connection issues.

    $ sudo -iu postgres
    $ cd data 
    # or
    $ cd <version>/data
    $ cat pg_hba.conf

Make sure that the first matching rule allows you to connect. If there are no rules that
allow you to connect from the dev server, add a rule like the following to the
pg_hba.conf:

    host    <username>_lab  <username>      dev.oscar.priv          trust

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

Since you likely don't have permissions to access the production database, you will need
to get a dump of the database from another lab member with access.  

    $ psql <username>_lab < [dump_file_name]
    
Your database should now be populated with production values (users, workitems, jobs, etc.)


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
