# lab.oscar #

This is the site code for lab.oscar.ncsu.edu


## Overview ##

These instructions exist to help get developers started on lab apps
development. It's unlikely that the main site folder will require much modification.

## Layout ##

    /deploy  - contains deployment scripts, secrets
    /labsite - site configuration files
    /foodapp - food ordering app
    /worklog - work tracking app


## Quickstart ##

This is a guide to start developing lab.oscar apps. It assumes basic linux command line knowledge.

First, you'll want to clone the repository and setup your
[virtualenv](http://www.virtualenv.org/en/latest/). 

    $ git clone git@github.com:ITNG/labsite
    $ cd labsite
    $ virtualenv .env

Activate the environment and install the site requirements. 

    $ source .env/bin/activate
    $ pip install -r requirements.pip

Setup postgres user and database:

    $ sudo -u postgres createuser --no-super --createdb --no-createrole <user>
    $ sudo -u postgres createdb <user>_lab

Setup Celery user:

    $ sudo rabbitmqctl add_user <user> ""
    $ sudo rabbitmqctl add_vhost <user>_lab
    $ sudo rabbitmqctl set_permissions -p <user>_lab <user> ".*" ".*" ".*"

Ensure that the new RabbitMQ user has the appropriate configuration:

    $ sudo rabbitmqctl list_permissions -p <user>_lab

Output should match:

    "<user>	.*	.*	.*"

You need your own django settings file.  This project comes with a sample that
you should start from.  You'll need to modify your celery and postgres settings
at the least, and generate a secret_key value.

    $ cp settings.ex.py settings.py
    $ vim settings.py

Next we need to create the database schema. When it asks you to create a user,
answer NO.  We will do this later.

    $ python manage.py syncdb
    $ python manage.py migrate --all

Now that the database is setup, we can add a user:

    $ python manage.py createsuperuser

To run the development server, use the manage.py runserver command:

    $ python manage.py runserver 0.0.0.0:<port>


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

