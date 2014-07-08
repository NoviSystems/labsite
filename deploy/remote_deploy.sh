#!/bin/bash

function usage {
    echo "Usage: $0 [user@]hostname [-b labsite branch] [-f foodapp branch] [-w worklog branch]"
}

args=("$@")

echo "remote deploy args: $@"

if [ $# == 1 ]; then
    SERVER=$1
elif [ $# -gt 1 ]; then
    SERVER=$1
    for (( i = 0; i<$#; i++ )) do
        if [ ${args[i]} = "-b" ]; then
            BRANCH="${args[i+1]}"
        elif [ ${args[i]} = "-s" ]; then
            echo "Setting deploy settings..."
            echo "$@"
            DEPLOY_SETTINGS="${args[i+1]}"
            echo "Using deploy settings in: $DEPLOY_SETTINGS..."
        elif [ ${args[i]} = "-f" ]; then
            FOODAPP_BRANCH="${args[i + 1]}"
        elif [ ${args[i]} = "-w" ]; then
            WORKLOG_BRANCH="${args[i + 1]}"
            echo "using worklog branch $WORKLOG_BRANCH"
        fi
    done
fi

if [ -z "$DEPLOY_SETTINGS" ]; then
    if [[ "$SERVER" == *-stag* ]]; then
        DEPLOY_SETTINGS="stag"
        echo "Using stag settings..."
    elif [[ "$SERVER" == *-prod* ]]; then
        DEPLOY_SETTINGS="prod"
        echo "Using prod settings..."
    else
        echo "Settings decision failed. Either provide a settings file or a known hostname."
        echo "Exiting with great sadness..."
        usage
        exit
    fi
fi

if [ -z "$BRANCH" ]; then
    BRANCH="master"
fi

if [ -z "$FOODAPP_BRANCH" ]; then
    FOODAPP_BRANCH="master"
fi

if [ -z "$WORKLOG_BRANCH" ]; then
    WORKLOG_BRANCH="master"
fi

if [ -z "$SERVER" ]; then
    usage
    exit
fi

DIR=`dirname $0`


# setup control connection
ssh -tNfM -o 'ControlPath=~/.ssh/%r@%h:%p.conn' $SERVER

# uses existing connection, doesn't ask for password
scp -o 'ControlPath=~/.ssh/%r@%h:%p.conn' ${DIR}/pull_and_update.sh "${SERVER}:/tmp/pull_and_update.sh"
ssh -o 'ControlPath=~/.ssh/%r@%h:%p.conn' $SERVER -t "sudo -u labuser bash /tmp/pull_and_update.sh $BRANCH $DEPLOY_SETTINGS $FOODAPP_BRANCH $WORKLOG_BRANCH"
ssh -o 'ControlPath=~/.ssh/%r@%h:%p.conn' $SERVER -t "sudo rm /tmp/pull_and_update.sh"


# close the connection
ssh -o 'ControlPath=~/.ssh/%r@%h:%p.conn' -O exit $SERVER
exit $?
