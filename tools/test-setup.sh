#!/bin/bash
set -euxo pipefail
# Used by Zuul CI to perform extra bootstrapping

# Bumping system tox because version from CentOS 7 is too old
# We are not using pip --user due to few bugs in tox role which does not allow
# us to override how is called. Once these are addressed we will switch back
# non-sudo mode.
PYTHON=$(command -v python3 python | head -n1)

sudo "$PYTHON" -m pip install "tox>=3.14.6"
#
# Bootstrapping of services needed for testing, like docker or podman, is done
# via pre.yaml playbook from ansible-tox-molecule job:
# https://github.com/ansible/ansible-zuul-jobs/blob/master/playbooks/ansible-tox-molecule/pre.yaml
#
# test-setup.sh runs before that playbook.
