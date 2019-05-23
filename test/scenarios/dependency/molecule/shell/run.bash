#!/usr/bin/env bash

set -e

# Note(decentral1se): avoid network access when local path install supported
ansible-galaxy install \
	-vvv \
	--force \
	--roles-path ${MOLECULE_EPHEMERAL_DIRECTORY}/roles/ \
	--role-file ${MOLECULE_SCENARIO_DIRECTORY}/requirements.yml


exit 0
