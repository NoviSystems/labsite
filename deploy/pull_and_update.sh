#!/bin/bash

REPOSITORY_URL="https://github.com/ITNG/labsite.git"
ROOT_DIR="/opt/lab/"  # Must be absolute path
DEPLOY_DIR="${ROOT_DIR}temp/"
DEPLOY_USER="labuser"

function usage {
    echo "Usage: $0 [branch] [server environment] [foodapp branch] [worklog branch]"
}

if [ `whoami` != $DEPLOY_USER ]; then
    echo "Aborting: script must be run as $DEPLOY_USER" 
    exit -1
fi

if [ $# -lt 2 ]; then
    usage
    exit
else
    BRANCH=$1
    DEPLOY_SETTINGS=$2
    FOODAPP_BRANCH=$3
    WORKLOG_BRANCH=$4
fi

if [ -z "$BRANCH" ]; then
    BRANCH="master"
fi

echo "Setting up deployment directory..."
rm -rf $DEPLOY_DIR
mkdir $DEPLOY_DIR
cd $DEPLOY_DIR
git clone $REPOSITORY_URL
cd labsite
git checkout $BRANCH

bash ${DEPLOY_DIR}labsite/deploy/update.sh $BRANCH $DEPLOY_SETTINGS $FOODAPP_BRANCH $WORKLOG_BRANCH

cd $ROOT_DIR
rm -rf $DEPLOY_DIR
