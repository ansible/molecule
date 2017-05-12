#!/usr/bin/env bash

#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

# A very crude file to assist with testing.  Will refine over time.

DOCKER_NAME=static-instance-docker
DOCKER_HOSTNAME="${DOCKER_NAME}"
DOCKER_IMAGE_TAG="${DOCKER_IMAGE_TAG:-7}"
DOCKER_IMAGE="${DOCKER_IMAGE:-molecule_local/centos:${DOCKER_IMAGE_TAG}}"
DOCKER_CMD="${DOCKER_CMD:-sleep infinity}"


# Static Docker driver setup

docker stop $(docker ps | grep ${DOCKER_NAME} | awk '{print $1}')
docker rm $(docker ps -a | grep ${DOCKER_IMAGE} | awk '{print $1}')
docker run \
		-d \
		--name ${DOCKER_NAME} \
		--hostname ${DOCKER_HOSTNAME} \
		-it ${DOCKER_IMAGE} ${DOCKER_CMD}

# Static Vagrant driver setup

(
	cd test/
	vagrant destroy -f
	vagrant up
	vagrant ssh-config > /tmp/ssh-config-vagrant
)

# Static OpenStack driver setup

INSTANCE_NAME=static-instance-openstack
INSTANCE_IMAGE="${INSTANCE_IMAGE:-Ubuntu-16.04}"
INSTANCE_FLAVOR="${INSTANCE_FLAVOR:-NO-Nano}"
INSTANCE_NETWORK_NAME="${INSTANCE_NETWORK_NAME:-molecule}"
INSTANCE_SECURITY_GROUP_NAME="${INSTANCE_SECURITY_GROUP_NAME:-molecule}"
INSTANCE_KEYPAIR_NAME="${INSTANCE_KEYPAIR_NAME:-molecule_key}"
INSTANCE_KEYPAIR_PATH="${INSTANCE_KEYPAIR_PATH:-/tmp/molecule_ssh_key}"
INSTANCE_SSH_PORT=22
INSTANCE_USER=${INSTANCE_USER:-cloud-user}

openstack server delete ${INSTANCE_NAME}
openstack server create \
	--image ${INSTANCE_IMAGE} \
	--flavor ${INSTANCE_FLAVOR} \
	--network ${INSTANCE_NETWORK_NAME} \
	--security-group ${INSTANCE_SECURITY_GROUP_NAME} \
	--key-name ${INSTANCE_KEYPAIR_NAME} \
	${INSTANCE_NAME}

cat << EOF > /tmp/ssh-config-openstack
Host ${INSTANCE_NAME}
  HostName !CHANGE!
  User ${INSTANCE_USER}
  Port 22
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
  PasswordAuthentication no
  IdentityFile ${INSTANCE_KEYPAIR_PATH}
  IdentitiesOnly yes
  LogLevel FATAL
EOF


exit 0
