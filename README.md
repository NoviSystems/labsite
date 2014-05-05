# foodapp #


## Getting Started ##

Foodapp is a django application that exists within the labsite ecosystem. To develop foodapp, you first need to setup [labsite](https://github.com/ITNG/labsite).

These instructions assume that labsite was cloned into your home directory. Clone foodapp into your home directory.

    $ cd ~
    $ git clone git@github.com:ITNG/foodapp.git

A soft link between labsite and foodapp needs to exist so that the local changes to foodapp are visible to labsite.

    $ cd ~/labsite
    $ ln -s ~/foodapp/foodapp
    
