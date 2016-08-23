#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os
import sys

import yaml

from molecule import ansible_galaxy
from molecule import ansible_playbook
from molecule import util
from molecule.command import base
from molecule.command import create


class Converge(base.Base):
    """
    Provisions all instances defined in molecule.yml.

    Usage:
        converge [--platform=<platform>] [--provider=<provider>] [--tags=<tag1,tag2>...] [--debug]

    Options:
        --platform=<platform>  specify a platform
        --provider=<provider>  specify a provider
        --tags=<tag1,tag2>     comma separated list of ansible tags to target
        --debug                get more detail
    """

    def execute(self,
                idempotent=False,
                create_instances=True,
                create_inventory=True,
                exit=True,
                hide_errors=True):
        """
        :param idempotent: Optionally provision servers quietly so output can be parsed for idempotence
        :param create_inventory: Toggle inventory creation
        :param create_instances: Toggle instance creation
        :return: Provisioning output
        """
        if self.molecule._state.created:
            create_instances = False

        if self.molecule._state.converged:
            create_inventory = False

        if self.molecule._state.multiple_platforms:
            self.args['--platform'] = 'all'
        else:
            if self.args[
                    '--platform'] == 'all' and self.molecule._state.created:
                create_instances = True
                create_inventory = True

        if create_instances and not idempotent:
            command_args, args = util.remove_args(self.command_args, self.args,
                                                  ['--tags'])
            c = create.Create(command_args, args, self.molecule)
            c.execute()

        if create_inventory:
            self.molecule._create_inventory_file()

        # install role dependencies only during `molecule converge`
        if not idempotent and 'requirements_file' in self.molecule.config.config[
                'ansible'] and not self.molecule._state.installed_deps:
            galaxy = ansible_galaxy.AnsibleGalaxy(self.molecule.config.config)
            galaxy.install()
            self.molecule._state.change_state('installed_deps', True)

        ansible = ansible_playbook.AnsiblePlaybook(self.molecule.config.config[
            'ansible'])

        # params to work with driver
        for k, v in self.molecule.driver.ansible_connection_params.items():
            ansible.add_cli_arg(k, v)

        # target tags passed in via CLI
        if self.molecule._args.get('--tags'):
            ansible.add_cli_arg('tags', self.molecule._args['--tags'].pop(0))

        if idempotent:
            ansible.remove_cli_arg('_out')
            ansible.remove_cli_arg('_err')
            ansible.add_env_arg('ANSIBLE_NOCOLOR', 'true')
            ansible.add_env_arg('ANSIBLE_FORCE_COLOR', 'false')

            # Save the previous callback plugin if any.
            callback_plugin = ansible.env.get('ANSIBLE_CALLBACK_PLUGINS', '')

            # Set the idempotence plugin.
            if callback_plugin:
                ansible.add_env_arg(
                    'ANSIBLE_CALLBACK_PLUGINS',
                    callback_plugin + ':' + os.path.join(
                        sys.prefix,
                        'share/molecule/ansible/plugins/callback/idempotence'))
            else:
                ansible.add_env_arg('ANSIBLE_CALLBACK_PLUGINS', os.path.join(
                    sys.prefix,
                    'share/molecule/ansible/plugins/callback/idempotence'))

        ansible.bake()
        if self.molecule._args.get('--debug'):
            ansible_env = {k: v
                           for (k, v) in ansible.env.items() if 'ANSIBLE' in k}
            other_env = {k: v
                         for (k, v) in ansible.env.items()
                         if 'ANSIBLE' not in k}
            util.debug('OTHER ENVIRONMENT',
                       yaml.dump(other_env,
                                 default_flow_style=False,
                                 indent=2))
            util.debug('ANSIBLE ENVIRONMENT',
                       yaml.dump(ansible_env,
                                 default_flow_style=False,
                                 indent=2))
            util.debug('ANSIBLE PLAYBOOK', str(ansible._ansible))

        util.print_info("Starting Ansible Run ...")
        status, output = ansible.execute(hide_errors=hide_errors)
        if status is not None:
            if exit:
                util.sysexit(status)
            return status, None

        if not self.molecule._state.converged:
            self.molecule._state.change_state('converged', True)

        return None, output
