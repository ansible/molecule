#!/usr/bin/env bash

set -e

# ignore errors added due to https://github.com/ansible/galaxy/issues/2030
ansible-galaxy install \
	-vvv \
	--ignore-errors \
	--force \
	--roles-path ${MOLECULE_EPHEMERAL_DIRECTORY}/roles/ \
	--role-file ${MOLECULE_SCENARIO_DIRECTORY}/requirements.yml

exit 0
