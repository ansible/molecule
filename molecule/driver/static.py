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


class Static(base.Base):
    """
    The class responsible for managing static instances.  Static is `not` the
    default driver used in Molecule.

    Under this driver, Molecule skips the provisioning/deprovisioning steps.
    It is the developers responsibility to manage the instances, and properly
    configure Molecule to connect to said instances.

    .. code-block:: yaml

        driver:
          name: static

    Use Molecule with statically created Docker instances.

    .. code-block:: bash

        $ docker run \\
            -d \\
            --name static-instance-docker \\
            --hostname static-instance-docker \\
            -it molecule_local/ubuntu:latest sleep infinity & wait

    .. code-block:: yaml

        driver:
          name: static
          options:
            login_cmd_template: 'docker exec -ti {} bash'
            ansible_connection_options:
              ansible_connection: docker
        platforms:
          - name: static-instance-default


    Use Molecule with statically created Vagrant instances.

    .. code-block:: yaml

        TODO

    .. note::

        Molecule automatically appends the scenario name to the instances it is
        testing.  It doesn't seem useful to converge each scenario against the
        same static host.
    """

    def __init__(self, config):
        super(Static, self).__init__(config)

    @property
    def name(self):
        return 'static'

    @property
    def login_cmd_template(self):
        return self.options['login_cmd_template']

    @property
    def safe_files(self):
        return []

    def login_args(self, instance_name):
        return [instance_name]

    def ansible_connection_options(self, instance_name):
        return self.options['ansible_connection_options']
