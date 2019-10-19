#  Copyright (c) 2019 Red Hat, Inc.
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

from molecule import logger, util
from molecule.api import Driver
from molecule.util import lru_cache
from molecule.util import sysexit_with_message

log = logger.get_logger(__name__)


class HetznerCloud(Driver):
    """
    The class responsible for managing `Hetzner Cloud`_ instances.
    `Hetzner Cloud`_ is **not** the default driver used in Molecule.

    Molecule leverages Ansible's `hcloud_server module`_, by mapping variables
    from ``molecule.yml`` into ``create.yml`` and ``destroy.yml``.

    .. important::

        The ``hcloud_server`` module is only available in Ansible >= 2.8.

    .. _`hcloud_server module`: https://docs.ansible.com/ansible/devel/modules/hcloud_server_module.html#hcloud-server-module

    .. code-block:: yaml

        driver:
          name: hetznercloud
        platforms:
          - name: instance
            server_type: cx11
            image: debian-9

    .. code-block:: bash

        $ pip install 'molecule[hetznercloud]'

    Change the options passed to the ssh client.

    .. code-block:: yaml

        driver:
          name: hetznercloud
          ssh_connection_options:
            - '-o ControlPath=~/.ansible/cp/%r@%h-%p'

    .. important::

        The Hetzner Cloud driver implementation uses the Parmiko transport
        provided by Ansible to avoid issues of connection hanging and
        indefinite polling as experienced with the default OpenSSh based
        transport.

    .. important::

        Molecule does not merge lists, when overriding the developer must
        provide all options.

    Provide the files Molecule will preserve upon each subcommand execution.

    .. code-block:: yaml

        driver:
          name: hetznercloud
          safe_files:
            - foo
    """  # noqa

    def __init__(self, config=None):
        super(HetznerCloud, self).__init__(config)
        self._name = 'hetznercloud'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
        connection_options = ' '.join(self.ssh_connection_options)

        return (
            'ssh {{address}} '
            '-l {{user}} '
            '-p {{port}} '
            '-i {{identity_file}} '
            '{}'
        ).format(connection_options)

    @property
    def default_safe_files(self):
        return [self.instance_config]

    @property
    def default_ssh_connection_options(self):
        return self._get_ssh_connection_options()

    def login_options(self, instance_name):
        d = {'instance': instance_name}

        return util.merge_dicts(d, self._get_instance_config(instance_name))

    def ansible_connection_options(self, instance_name):
        try:
            d = self._get_instance_config(instance_name)

            return {
                'ansible_user': d['user'],
                'ansible_host': d['address'],
                'ansible_port': d['port'],
                'ansible_private_key_file': d['identity_file'],
                'connection': 'ssh',
                'ansible_ssh_common_args': ' '.join(self.ssh_connection_options),
            }
        except StopIteration:
            return {}
        except IOError:
            # Instance has yet to be provisioned , therefore the
            # instance_config is not on disk.
            return {}

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(self._config.driver.instance_config)

        return next(
            item for item in instance_config_dict if item['instance'] == instance_name
        )

    @lru_cache()
    def sanity_checks(self):
        """Hetzner Cloud driver sanity checks."""

        log.info("Sanity checks: '{}'".format(self._name))

        try:
            import hcloud  # noqa
        except ImportError:
            msg = (
                'Missing Hetzner Cloud driver dependency. Please '
                "install via 'molecule[hetznercloud]' or refer to "
                'your INSTALL.rst driver documentation file'
            )
            sysexit_with_message(msg)

        if 'HCLOUD_TOKEN' not in os.environ:
            msg = (
                'Missing Hetzner Cloud API token. Please expose '
                'the HCLOUD_TOKEN environment variable with your '
                'account API token value'
            )
            sysexit_with_message(msg)
