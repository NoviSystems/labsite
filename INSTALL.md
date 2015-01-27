
## Dependencies ##

Yum Dependencies:
* python
* python-virtualenv
* postgresql-server
* postgresql-devel
* git
* supervisor
* nginx
* rabbitmq-server
* ntp

All other dependencies will be installed through pip in a virtual environment.


## Lab user ##

Create the labuser user:

    $ sudo useradd labuser -d /opt/lab/ --shell /bin/bash


## Sudoers ##

The labuser user needs permissions to run certain commands, and the users on
the system need permissions to run pull_and_update.sh as the labuser.

Use visudo to edit the sudoers file:

    $ sudo visudo

If visudo complains about "no editor found", first make a link to where it
expects the editor to be:

    $ sudo ln /usr/bin/vi /bin/vi

Add the following at the end to sudoers, changing the DEPLOYUSERS user list
accordingly:

    # labuser permissions
    labuser ALL=(root)  NOPASSWD: /bin/chown -R labuser /opt/lab/*
    labuser ALL=(root)  NOPASSWD: /bin/chgrp -R labuser /opt/lab/*
    labuser ALL=(root)  NOPASSWD: /bin/chmod -R * /opt/lab/*
    labuser ALL=(root)  NOPASSWD: /bin/chmod * /opt/lab/*
    labuser ALL=(root)  NOPASSWD: /bin/mkdir /opt/lab
    labuser ALL=(root)  NOPASSWD: /sbin/service supervisord start
    labuser ALL=(root)  NOPASSWD: /sbin/service supervisord stop
    labuser ALL=(root)  NOPASSWD: /sbin/service nginx start
    labuser ALL=(root)  NOPASSWD: /sbin/service nginx stop

    # User permissions to deploy
    User_Alias DEPLOYUSERS = jbass
    DEPLOYUSERS    ALL=(labuser)      NOPASSWD: /home/deploy/p1t/deploy/pull_and_update.sh *

Anybody in the DEPLOYUSERS list will be able to deploy.


## Repository ##

The lab site is not currently located on github. The primary repo is located on
[staging](git@lab-stag.oscar.ncsu.edu:/opt/git/labsite.git)

In order for the labuser to pull from the repository, you need to generate
a key and give it access to the git user on staging.  Create the key like this:

    $ sudo -iu labuser
    $ ssh-keygen -t rsa     # Leave password blank

When complete, exit out of labuser to your username:

    $ exit

Repository access is handled through a git machine user. Add the newly created
public key to the git user's authorized_keys to give this machine access to
clone and pull.
In order to copy the production ssh key to the git user, you'll need to use an account
with access to your private key
On production: 

    $ sudo cp /opt/lab/.ssh/id_rsa.pub ~/labprod.pub
    $ sudo chown <user> labprod.pub
    $ sudo chgrp <user> labprod.pub

If your private key is located in your lab user account, then:
    
    $ scp ~/labprod.pub <user>@lab-stag.oscar.ncsu.edu:~/labprod.pub

Otherwise, use scp from your local machine:

    $ scp <user>@lab.oscar.ncsu.edu:~/labprod.pub ~/
    $ scp ~/labprod.pub <user>@lab-stag.oscar.ncsu.edu:~/labprod.pub
    $ rm ~/labprod.pub

On staging:
Copy the contents of the key from your user directory to the git user's
authorized_keys

    $ sudo cp ~/labprod.pub /opt/git/.ssh/labprod.pub
    $ sudo sh -c 'cat /opt/git/.ssh/labprod.pub >> /opt/git/.ssh/authorized_keys'
    $ sudo rm /opt/git/.ssh/labprod.pub

Now that labuser on production has permissions, login as labuser and clone the repo:

    $ sudo -iu labuser
    $ git clone git@lab-stag.oscar.ncsu.edu:/opt/git/labsite.git
    $ exit


## Postgres ##

Initialize postgres, start it, and configure to run on startup:

    $ sudo service postgresql-setup initdb
    $ sudo chkconfig postgresql on
    $ sudo service postgresql start

Configure the postgres user and database.  Ignore the warning "could not
change directory to..."

    $ sudo -iu postgres
    $ createuser labuser --no-superuser --no-createdb --no-createrole
    $ createdb labdb

Exit back to your regular user and restart the server
    $ exit
    $ sudo service postgresql restart

To configure permissions for any local user to log into the postgres
lab user, put this in /var/lib/pgsql/data/pg_hba.conf as the first
uncommented line:

    local labuser all trust


## Supervisord ##

Copy config_examples/supervisord.ini to /etc/supervisord.d/labsite.ini and
customize it if needed.

Configure to start on boot:

    $ sudo chkconfig supervisord on


## nginx ##

First you will need an ssl certificate.  You can generate your own by
following the instructions here:

http://www.server-world.info/en/note?os=Fedora_16&p=ssl

Note that the pass phrase given in the second command is arbitrary, since it
is removed by the third command.

Remove /etc/nginx/conf.d/default.conf, then copy config_examples/nginx.conf
into that directory and customize it.  You might need to change the
server_name if you want to redirect to a location other than your hostname.

Configure to start on boot:

    $ sudo chkconfig nginx on


## Firewall ##

Don't forget to let port 80 and 443 through!  To do this, edit
/etc/sysconfig/iptables and add these lines (insert immediately
preceding the REJECT statements):

    -A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT
    -A INPUT -m state --state NEW -m tcp -p tcp --dport 443 -j ACCEPT

Then restart iptables:

    $ sudo service iptables restart


## RabbitMQ ##

RabbitMQ is the message passing backend for celery.

Start RabbitMQ:

    $ sudo service rabbitmq-server start
    $ sudo chkconfig rabbitmq-server on

Create a user and vhost. Locate the password from labuser in
settings.py and assign it to the labuser upon creation:

    $ sudo rabbitmqctl add_user labuser "<password_from_settings.py>"
    $ sudo rabbitmqctl add_vhost lab_vhost
    $ sudo rabbitmqctl set_permissions -p lab_vhost labuser ".*" ".*" ".*"

Ensure that the new RabbitMQ user has been properly configured:

    $ sudo rabbitmqctl list_permissions -p lab_vhost

Output should match the permissions set for labuser.


## NTP Client ##

It is a good idea to use ntp to keep correct time:

    $ sudo yum install ntp
    $ sudo chkconfig ntpd on
    $ sudo ntpdate pool.ntp.org


## Configure daily database backups ##

These instructions describe how to set up daily backups that are rotated for 14 days.

1. take control of the root user:

    $ sudo su

2. make a directory for the backups:

    $ mkdir /var/log/lab_db_backup/

3. make the first backup

    $ sudo -u postgres pg_dump labdb > /var/log/lab_db_backup/lab_db_bu

4. config logrotate to take daily backups and rotate accordingly

    add the following to the end of /etc/logrotate.conf:

        /var/log/lab_db_backup/lab_db_bu {
            rotate 14
            daily
            postrotate
                sudo -u postgres pg_dump labdb > /var/log/lab_db_backup/lab_db_bu
            endscript
        }


## Troubleshooting  ##

Internal Server Error: 

    If lunchapp is serving an Internal Server Error, ensure that there is an 
    instance of a RiceCooker in the database. Login to the admin pages as a
    superuser and create a RiceCooker. Refresh the page.


