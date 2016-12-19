#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import re

import click
import yaml

from molecule import ansible_playbook
from molecule import util
from molecule.command import base
from molecule.command import create
from molecule.command import dependency


class Converge(base.Base):
    def execute(self,
                idempotent=False,
                create_instances=True,
                create_inventory=True,
                exit=True,
                hide_errors=True):
        """
        Execute the actions necessary to perform a `molecule converge` and
        return a tuple.

        :param idempotent: An optional flag to perform the converge again, and
         parse the output for idempotence.
        :param create_inventory: An optional flag to toggle inventory creation.
        :param create_instances: An optional flag to toggle instance creation.
        :return: Return a tuple of (`exit status`, `command output`), otherwise
         sys.exit on command failure.
        """
        debug = self.args.get('debug')

        if self.molecule.state.created:
            create_instances = False

        if self.molecule.state.converged:
            create_inventory = False

        if self.molecule.state.multiple_platforms:
            self.command_args['platform'] = 'all'
        else:
            if ((self.command_args.get('platform') == 'all') and
                    self.molecule.state.created):
                create_instances = True
                create_inventory = True

        if create_instances and not idempotent:
            c = create.Create(self.args, self.command_args, self.molecule)
            c.execute()

        if create_inventory:
            self.molecule.create_inventory_file()

        d = dependency.Dependency(self.args, self.command_args, self.molecule)
        d.execute()

        ansible = ansible_playbook.AnsiblePlaybook(
            self.molecule.config.config['ansible'],
            self.molecule.driver.ansible_connection_params,
            raw_ansible_args=self.command_args.get('ansible_args'),
            debug=debug)

        if idempotent:
            # Don't log stdout/err
            ansible.remove_cli_arg('_out')
            ansible.remove_cli_arg('_err')
            # Idempotence task regexp cannot handle diff
            ansible.remove_cli_arg('diff')
            # Disable color for regexp
            ansible.add_env_arg('ANSIBLE_NOCOLOR', 'true')
            ansible.add_env_arg('ANSIBLE_FORCE_COLOR', 'false')

        if debug:
            ansible_env = {
                k: v
                for (k, v) in ansible.env.items() if 'ANSIBLE' in k
            }
            util.print_debug(
                'ANSIBLE ENVIRONMENT',
                yaml.dump(
                    ansible_env, default_flow_style=False, indent=2))

        util.print_info('Starting Ansible Run...')
        status, output = ansible.execute(hide_errors=hide_errors)

        if idempotent:
            if output is None:
                util.print_info('Skipping due to errors during converge.')
                return 1, '', ''
            if self._is_idempotent(output):
                util.print_success('Idempotence test passed.')
                return 0, '', ''
            else:
                msg = ('Idempotence test failed because of the following '
                       'tasks:\n{}')
                err_tasks = '\n'.join(self._non_idempotent_tasks(output))
                util.print_error(msg.format(err_tasks))
                errors = msg.format(err_tasks)
                return 1, errors, ''

        if status is not None:
            if exit:
                util.sysexit(status)
            return status, '', ''

        if not self.molecule.state.converged:
            self.molecule.state.change_state('converged', True)

        return 0, '', ''

    def _is_idempotent(self, output):
        """
        Parses the output of the provisioning for changed and returns a bool.

        :param output: A string containing the output of the ansible run.
        :return: bool
        """

        # Remove blank lines to make regex matches easier
        output = re.sub("\n\s*\n*", "\n", output)

        # Look for any non-zero changed lines
        changed = re.search(r'(changed=[1-9][0-9]*)', output)

        if changed:
            # Not idempotent
            return False

        return True

    def _non_idempotent_tasks(self, output):
        """
        Parses the output to identify the non idempotent tasks.

        :param (str) output: A string containing the output of the ansible run.
        :return: A list containing the names of the non idempotent tasks.
        """
        # Remove blank lines to make regex matches easier.
        output = re.sub("\n\s*\n*", "\n", output)

        # Split the output into a list and go through it.
        output_lines = output.split('\n')
        res = []
        task_line = ''
        for idx, line in enumerate(output_lines):
            if line.startswith('TASK'):
                task_line = line
            elif line.startswith('changed'):
                host_name = re.search(r'\[(.*)\]', line).groups()[0]
                task_name = re.search(r'\[(.*)\]', task_line).groups()[0]
                res.append('* [{}] => {}'.format(host_name, task_name))

        return res


@click.command()
@click.option('--driver', default=None, help='Specificy a driver.')
@click.option('--platform', default=None, help='Specify a platform.')
@click.option('--provider', default=None, help='Specify a provider.')
@click.argument('ansible_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def converge(ctx, driver, platform, provider,
             ansible_args):  # pragma: no cover
    """ Provisions all instances defined in molecule.yml. """
    command_args = {
        'driver': driver,
        'platform': platform,
        'provider': provider,
        'ansible_args': ansible_args
    }

    c = Converge(ctx.obj.get('args'), command_args)
    c.execute
    util.sysexit(c.execute()[0])
