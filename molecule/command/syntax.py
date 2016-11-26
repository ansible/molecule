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

import click

from molecule import ansible_playbook
from molecule import util
from molecule.command import base
from molecule.command import dependency


class Syntax(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule syntax` and
        return a tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple provided by :meth:`.AnsiblePlaybook.execute`.
        """
        debug = self.args.get('debug')
        self.molecule.create_templates()
        d = dependency.Dependency(self.args, self.command_args, self.molecule)
        d.execute()

        ansible = ansible_playbook.AnsiblePlaybook(
            self.molecule.config.config['ansible'], {}, debug=debug)
        ansible.add_cli_arg('syntax-check', True)
        ansible.add_cli_arg('inventory_file', 'localhost,')
        util.print_info("Checking playbook's syntax...")

        return ansible.execute(hide_errors=True)


@click.command()
@click.pass_context
def syntax(ctx):  # pragma: no cover
    """ Performs a syntax check on the current role. """
    s = Syntax(ctx.obj.get('args'), {})
    s.execute
    util.sysexit(s.execute()[0])
