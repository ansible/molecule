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

from molecule import logger
from molecule.driver import base

LOG = logger.get_logger(__name__)


class Delegated(base.Base):
    """
    The class responsible for managing delegated instances.  Delegated is `not`
    the default driver used in Molecule.

    Under this driver, it is the developers responsibility to implement the
    create and destroy actions.

    .. code-block:: yaml

        driver:
          name: delegated

    Molecule can also skip the provisioning/deprovisioning steps.  It is the
    developers responsibility to manage the instances, and properly configure
    Molecule to connect to said instances.

    .. code-block:: yaml

        driver:
          name: delegated
          options:
            managed: False
            login_cmd_template: 'docker exec -ti {instance} bash'
            ansible_connection_options:
              connection: docker
        platforms:
          - name: instance-docker

    .. code-block:: bash

        $ docker run \\
            -d \\
            --name instance-docker \\
            --hostname instance-docker \\
            -it molecule_local/ubuntu:latest sleep infinity & wait

    Use Molecule with delegated instances, which are accessible over ssh.

    .. important::

        It is the developers responsibility to configure the ssh config file.

    .. code-block:: yaml

        driver:
          name: delegated
          options:
            managed: False
            login_cmd_template: 'ssh {instance} -F /tmp/ssh-config'
            ansible_connection_options:
              connection: ssh
              ansible_ssh_common_args -F /path/to/ssh-config
        platforms:
          - name: instance-vagrant

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: delegated
          safe_files:
            - foo
            - .molecule/bar
    """

    def __init__(self, config):
        super(Delegated, self).__init__(config)
        self._name = 'delegated'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
        return self.options['login_cmd_template']

    @property
    def default_safe_files(self):
        return []

    @property
    def default_ssh_connection_options(self):
        return []

    def login_options(self, instance_name):
        return {'instance': instance_name}

    def ansible_connection_options(self, instance_name):
        return self.options['ansible_connection_options']
