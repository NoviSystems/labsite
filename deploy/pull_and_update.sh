#!/bin/bash
set -o errexit

REPOSITORY_URL="git@lab-stag.oscar.ncsu.edu:/opt/git/labsite.git"
ROOT_DIR="/opt/lab/"  # Must be absolute path
DEPLOY_DIR="${ROOT_DIR}temp/"
DEPLOY_USER="labuser"

function usage {
    echo "Usage: $0 [branch] [server environment]"
}

if [ `whoami` != $DEPLOY_USER ]; then
    echo "Aborting: script must be run as $DEPLOY_USER" 
    exit -1
fi

if [ $# -ne 2 ]; then
    usage
    exit
else
    BRANCH=$1
    DEPLOY_SETTINGS=$2
fi

if [ -z "$BRANCH" ]; then
    BRANCH="master"
fi

echo "Setting up deployment directory..."
rm -rf $DEPLOY_DIR
mkdir $DEPLOY_DIR
cd $DEPLOY_DIR
git clone $REPOSITORY_URL

bash ${DEPLOY_DIR}labsite/deploy/update.sh $BRANCH $DEPLOY_SETTINGS

cd $ROOT_DIR
rm -rf $DEPLOY_DIR
