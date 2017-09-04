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
    The class responsible for managing `Vagrant`_ instances.  `Vagrant`_ is
    `not` the default driver used in Molecule.

    Molecule leverages Molecule's own :ref:`molecule_vagrant_module`, by
    mapping variables from `molecule.yml` into `create.yml` and `destroy.yml`.

    .. important::

        This driver is alpha quality software.  Do not perform any additonal
        tasks inside the `create` playbook.  Molecule does not know about the
        Vagrant instances' configuration until the `converge` playbook is
        executed.

        The `create` playbook boots instances, then the instance data is
        written to disk.  The instance data is then added to Molecule's Ansible
        inventory on the next execution of `molecule.command.create`, which
        happens to be the `converge` playbook.

        This is an area needing improvement.  Gluing togher Ansible playbook
        return data and molecule is clunky.  Moving the playbook execution
        from `sh` to python is less than ideal, since the playbook's return
        data needs handled by an internal callback plugin.

        Operating this far inside Ansible's internals doesn't feel right.  Nor
        does orchestrating Ansible's CLI with Molecule.  Ansible is throwing
        pieces over the wall, which Molecule is picking up and reconstructing.

    .. code-block:: yaml

        driver:
          name: vagrant
        platforms:
          - name: instance
            instance_name: "{{ item.name }}"
            instance_interfaces: "{{ item.interfaces | default(omit) }}"
            instance_raw_config_args: "{{ item.instance_raw_config_args | default(omit) }}"
            platform_box: "{{ item.box }}"
            platform_box_version: "{{ item.box_version | default(omit) }}"
            platform_box_url: "{{ item.box_url | default(omit) }}"
            provider_name: "{{ molecule_yml.driver.provider.name }}"
            provider_memory: "{{ item.memory | default(omit) }}"
            provider_cpus: "{{ item.cpus | default(omit) }}"
            provider_raw_config_args: "{{ item.raw_config_args | default(omit) }}"

    .. code-block:: bash

        $ sudo pip install python-vagrant

    Change the provider passed to Vagrant.

    .. code-block:: yaml

        driver:
          name: vagrant
          provider:
            name: parallels

    Change the options passed to the ssh client.

    .. code-block:: yaml

        driver:
          name: vagrant
          ssh_connection_options:
            -o ControlPath=~/.ansible/cp/%r@%h-%p

    .. important::

        Molecule does not merge lists, when overriding the developer must
        provide all options.

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: vagrant
          safe_files:
            - foo
            - .molecule/bar

    .. _`Vagrant`: https://www.vagrantup.com
    """  # noqa

    def __init__(self, config):
        super(Vagrant, self).__init__(config)
        self._name = 'vagrant'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def testinfra_options(self):
        return {
            'connection': 'ansible',
            'ansible-inventory': self._config.provisioner.inventory_file
        }

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
            self.vagrantfile,
            self.vagrantfile_config,
            self.instance_config,
            os.path.join(self._config.scenario.ephemeral_directory,
                         '.vagrant'),
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

    @property
    def vagrantfile(self):
        return os.path.join(self._config.scenario.ephemeral_directory,
                            'Vagrantfile')

    @property
    def vagrantfile_config(self):
        return os.path.join(self._config.scenario.ephemeral_directory,
                            'vagrant.yml')

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(
            self._config.driver.instance_config)

        return next(item for item in instance_config_dict
                    if item['instance'] == instance_name)
