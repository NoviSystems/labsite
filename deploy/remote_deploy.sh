#!/bin/bash

function usage {
    echo "Usage: $0 [user@]hostname [branch]"
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

if [ -z "$SERVER" ]; then
    usage
    exit
fi

DIR=`dirname $0`


# setup control connection
ssh -tNfM -o 'ControlPath=~/.ssh/%r@%h:%p.conn' $SERVER

# uses existing connection, doesn't ask for password
scp -o 'ControlPath=~/.ssh/%r@%h:%p.conn' ${DIR}/pull_and_update.sh "${SERVER}:/tmp/pull_and_update.sh"
ssh -o 'ControlPath=~/.ssh/%r@%h:%p.conn' $SERVER -t "sudo -u labuser bash /tmp/pull_and_update.sh $BRANCH $DEPLOY_SETTINGS"


# close the connection
ssh -o 'ControlPath=~/.ssh/%r@%h:%p.conn' -O exit $SERVER
exit $?
