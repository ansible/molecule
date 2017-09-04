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

from molecule import util

LOG = logger.get_logger(__name__)


class Openstack(base.Base):
    """
    The class responsible for managing `OpenStack`_ instances.  `OpenStack`_
    is `not` the default driver used in Molecule.

    Molecule leverages Ansible's `openstack_module`_, by mapping variables
    from `molecule.yml` into `create.yml` and `destroy.yml`.

    .. _`openstack_module`: http://docs.ansible.com/ansible/latest/os_server_module.html

    .. code-block:: yaml

        driver:
          name: openstack
        platforms:
          - name: instance
            image: "{{ item.image }}"
            flavor: "{{ item.flavor }}"
            security_groups: "{{ security_group_name }}"
            key_name: "{{ keypair_name }}"
            nics:
              - net-id: "{{ openstack_networks[0]['id'] }}"

    .. code-block:: bash

        $ sudo pip install shade

    Change the options passed to the ssh client.

    .. code-block:: yaml

        driver:
          name: openstack
          ssh_connection_options:
            -o ControlPath=~/.ansible/cp/%r@%h-%p

    .. important::

        Molecule does not merge lists, when overriding the developer must
        provide all options.

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: openstack
          safe_files:
            - foo
            - .molecule/bar

    .. _`OpenStack`: https://www.openstack.org
    """  # noqa

    def __init__(self, config):
        super(Openstack, self).__init__(config)
        self._name = 'openstack'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
        connection_options = ' '.join(self.ssh_connection_options)

        return ('ssh {{address}} '
                '-l {{user}} '
                '-p {{port}} '
                '-i {{identity_file}} '
                '{}').format(connection_options)

    @property
    def default_safe_files(self):
        return [
            self.instance_config,
        ]

    @property
    def default_ssh_connection_options(self):
        return self._get_ssh_connection_options()

    def login_options(self, instance_name):
        d = {'instance': instance_name}

        return self._config.merge_dicts(
            d, self._get_instance_config(instance_name))

    def ansible_connection_options(self, instance_name):
        try:
            d = self._get_instance_config(instance_name)

            return {
                'ansible_user': d['user'],
                'ansible_host': d['address'],
                'ansible_port': d['port'],
                'ansible_private_key_file': d['identity_file'],
                'connection': 'ssh',
                'ansible_ssh_common_args':
                ' '.join(self.ssh_connection_options),
            }
        except StopIteration:
            return {}
        except IOError:
            # Instance has yet to be provisioned , therefore the
            # instance_config is not on disk.
            return {}

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(
            self._config.driver.instance_config)

        return next(item for item in instance_config_dict
                    if item['instance'] == instance_name)
