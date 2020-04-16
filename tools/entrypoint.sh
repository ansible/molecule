#!/bin/bash

# install mounted molecule repo
pip3 install -e .

# start docker daemon
dockerd-entrypoint.sh &>/var/log/dockerd.log