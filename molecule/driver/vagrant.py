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

import os

from molecule import logger
from molecule import util
from molecule.driver import base

LOG = logger.get_logger(__name__)


class Vagrant(base.Base):
    """
    `Vagrant`_ is `not` the default driver.

    .. code-block:: yaml

        driver:
          name: vagrant

    .. code-block:: bash

        $ pip install python-vagrant

    .. _`Vagrant`: https://www.vagrantup.com
    """

    def __init__(self, config):
        super(Vagrant, self).__init__(config)

    @property
    def testinfra_options(self):
        return {
            'connection': 'ansible',
            'ansible-inventory': self._config.provisioner.inventory_file
        }

    @property
    def login_cmd_template(self):
        return 'ssh {} -l {} -p {} -i {}'

    @property
    def safe_files(self):
        return [
            self.vagrantfile, self.vagrantfile_config, self.instance_config
        ]

    def login_args(self, instance_name):
        d = self._get_instance_config(instance_name)

        return [d['HostName'], d['User'], d['Port'], d['IdentityFile']]

    def connection_options(self, instance_name):
        try:
            d = self._get_instance_config(instance_name)

            return {
                'ansible_ssh_user': d['User'],
                'ansible_ssh_host': d['HostName'],
                'ansible_ssh_port': d['Port'],
                'ansible_ssh_private_key_file': d['IdentityFile'],
                'connection': 'ssh'
            }
        except StopIteration:
            return {}
        except IOError:
            # Instance has yet to be provisioned , therefore the
            # instance_config is not on disk.
            return {}

    @property
    def vagrantfile(self):
        return os.path.join(self._config.ephemeral_directory, 'Vagrantfile')

    @property
    def vagrantfile_config(self):
        return os.path.join(self._config.ephemeral_directory, 'vagrant.yml')

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(
            self._config.driver.instance_config)

        return next(item for item in instance_config_dict.get('results', {})
                    if item['Host'] == instance_name)
