
## What is Deployment? ##

Deployment ``does not`` copy your working tree to a server.  Deployment will
update a server's installation to a particular revision in git.  By default
the server is updated to master, but you can deploy a server to a different
branch.


## How to Deploy ##

Before deploying, make sure you've updated and committed
``deploy/settings.py``.  To deploy, use the ``remote_deploy.sh``, giving the
remote server as the first argument:

    $ ./remote_deploy.sh lab-stag.oscar.ncsu.edu

To specify a branch specify it in the second argument:

    $ ./remote_deploy.sh lab-stag.oscar.ncsu.edu unstable
