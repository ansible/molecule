#!/bin/bash

# install mounted molecule repo
pip3 install -e .

# start docker daemon
echo "Starting docker daemon..."
dockerd-entrypoint.sh &> /var/log/dockerd.log &

echo "Waiting for docker daemon..."
retry=0
timeout=20 #sec
docker info &> /dev/null
while [ $? -eq 1 ]
    do
    if [ $retry -gt  $timeout ]; then
        echo "Daemon failed to spawn after $timeout sec"
        exit
    fi
    sleep 1
    ((retry++))
    docker info &> /dev/null
done

exec $@