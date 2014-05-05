#!/bin/bash
set -o errexit
set -o nounset

whoami

REPOSITORY_URL="https://github.com/ITNG/labsite"
ROOT_DIR="/opt/lab/"  # Must be absolute path
PROJECT_DIR="${ROOT_DIR}labsite/"
BACKUP_DIR="${ROOT_DIR}backup/"
DEPLOY_DIR="${ROOT_DIR}temp/"
DEPLOY_SETTINGS_DIR="${DEPLOY_DIR}labsite/deploy/"

function usage {
    echo "Usage: $0 [branch] [server environment]"
}

if [ $# -ne 2 ]; then
    usage
    exit
else
    BRANCH=$1
    DEPLOY_SETTINGS="${DEPLOY_SETTINGS_DIR}$2_settings.py"
fi

PROJECT_FILES_USER=labuser
PROJECT_FILES_GROUP=labuser
PROJECT_FILES_OCTAL=775

function project_dir_permissions {
    if [ ! -d $PROJECT_DIR ]; then
        sudo mkdir $PROJECT_DIR
    fi
    sudo chown -R $PROJECT_FILES_USER $PROJECT_DIR
    sudo chgrp -R $PROJECT_FILES_GROUP $PROJECT_DIR
    sudo chmod -R $PROJECT_FILES_OCTAL $PROJECT_DIR
}

function create_files {
    if [ ! -d $PROJECT_DIR/log ]; then
        mkdir $PROJECT_DIR/log
    fi
    # fix supervisor issues
    touch /opt/lab/labsite/log/{celerybeat,celeryd}.log

    chmod  $PROJECT_FILES_OCTAL $PROJECT_DIR/log
    chmod -R $PROJECT_FILES_OCTAL $PROJECT_DIR/log

}


# Backup current project
if [ -a $PROJECT_DIR ]; then
    echo "Backing up project..."
    rm -rf $BACKUP_DIR
    git clone --no-hardlinks $PROJECT_DIR $BACKUP_DIR

    if [ -d ${PROJECT_DIR}.env ]; then
        set +o nounset
        source ${PROJECT_DIR}.env/bin/activate
        echo `pip freeze` > ${BACKUP_DIR}env_state.pip
        sed -e 's/\s\+/\n/g' ${BACKUP_DIR}env_state.pip > tmpfile ; mv tmpfile ${BACKUP_DIR}env_state.pip
        deactivate
        set -o nounset
    fi
fi


# Clone project or update
if [ ! -d $PROJECT_DIR/.git ]; then
    echo "Cloning repository..."
    git clone $REPOSITORY_URL $PROJECT_DIR
    cd $PROJECT_DIR
    git checkout $BRANCH
else
    echo "Updating repository..."
    cd $PROJECT_DIR

    set +o errexit      # git diff 'fails' if submodules are outdated. 
    DIRTY=`git diff-index --quiet HEAD`
    set -o errexit
    if [ $DIRTY ]; then
        echo "Stashing changes..."
        git stash       # stash any changes (secrets, etc.. ) so checkout/pull doesn't fail
    fi
    
    git fetch
    git checkout $BRANCH
    git pull origin

    if [ $DIRTY ]; then
        git stash pop
    fi
fi

# Create Virtual Environment
if [ ! -d $PROJECT_DIR/.env ]; then
    echo "virtualenv not found, creating one..."
    virtualenv ${PROJECT_DIR}.env
fi

# Activate Virtual Environment
echo "Activating virtualenv..."
set +o nounset  # env activate fails with nounset, temporarily disable it
source ${PROJECT_DIR}.env/bin/activate
set -o nounset

# Stop Servers
sudo /sbin/service supervisord stop
sudo /sbin/service nginx stop

# Pip requirements
if [ -f ${PROJECT_DIR}requirements.pip ]; then
    echo "Installing project requirements..."
    pip install -q -r ${PROJECT_DIR}requirements.pip
else
    echo "No project requirements.pip found..."
fi

echo "Installing requirements from ${PROJECT_DIR} ..."
pip install -q -r ${PROJECT_DIR}/requirements.pip

# Copy settings file
# settings.py in the deployment repo will have to be updated if the project's
# settings.py.sample file changes.
echo "Copying deploy settings from ${DEPLOY_SETTINGS} to ${PROJECT_DIR}labsite/settings.py"
cp ${DEPLOY_SETTINGS} ${PROJECT_DIR}labsite/settings.py

# Create secret key
# The secret_key file is read in by settings.py
if [ ! -f ${PROJECT_DIR}labsite/secret_key ]; then
    echo "No secret key found, creating one"
    cat /dev/urandom | tr -cd [:print:] | head -c 64 >> ${PROJECT_DIR}labsite/secret_key
fi

# Create secrets file
if [ ! -f ${PROJECT_DIR}labsite/secrets.py ]; then
    echo "No secrets file found, creating one"
    touch ${PROJECT_DIR}labsite/secrets.py
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    echo "@@@                                 @@@"
    echo "@@@ BE SURE TO CONFIGURE SECRETS.PY @@@"
    echo "@@@                                 @@@"
    echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
fi

# Collect static
# Make sure to have the collectstatic app in settings.INSTALLED_APPS.  The STATIC_ROOT must be $PROJECT_DIR/static-root/
# echo "Collecting static files."
python $PROJECT_DIR/manage.py collectstatic --noinput
# python $PROJECT_DIR/manage.py compress --force

# project_dir_permissions
create_files
# project_dir_permissions

# Django Synchdb
python ${PROJECT_DIR}manage.py syncdb --noinput
python ${PROJECT_DIR}manage.py migrate --all --noinput --no-initial-data

# Start Servers!
sudo /sbin/service supervisord start
sudo /sbin/service nginx start