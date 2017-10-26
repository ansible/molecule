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


class Lxd(base.Base):
    """
    The class responsible for managing `LXD`_ containers.  `LXD`_ is `not` the
    default driver used in Molecule.

    Molecule leverages Ansible's `lxd_container`_ module, by mapping variables
    from `molecule.yml` into `create.yml` and `destroy.yml`.

    .. _`lxd_container`: http://docs.ansible.com/ansible/latest/lxd_container_module.html

    .. code-block:: yaml

        driver:
          name: lxd

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: lxd
          safe_files:
            - foo
            - .molecule/bar

    .. _`LXD`: https://linuxcontainers.org/lxd/introduction/
    """  # noqa

    def __init__(self, config):
        super(Lxd, self).__init__(config)
        self._name = 'lxd'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
        return 'lxc exec {instance} bash'

    @property
    def default_safe_files(self):
        return []

    @property
    def default_ssh_connection_options(self):
        return []

    def login_options(self, instance_name):
        return {'instance': instance_name}

    def ansible_connection_options(self, instance_name):
        return {'ansible_connection': 'lxd'}
