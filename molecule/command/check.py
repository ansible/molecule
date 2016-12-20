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


class Check(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions necessary to perform a `molecule check` and
        return a tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple provided by :meth:`.AnsiblePlaybook.execute`.
        """
        if not self.molecule.state.created:
            msg = ('Instance(s) not created, `check` should be run '
                   'against created instance(s).')
            util.print_error(msg)
            util.sysexit()

        debug = self.args.get('debug')
        ansible = ansible_playbook.AnsiblePlaybook(
            self.molecule.config.config['ansible'],
            self.molecule.driver.ansible_connection_params,
            debug=debug)
        ansible.add_cli_arg('check', True)

        util.print_info("Performing a 'Dry Run' of playbook...")
        (ret_code, output) = ansible.execute(hide_errors=True)
        return ret_code, '', ''


@click.command()
@click.pass_context
def check(ctx):  # pragma: no cover
    """ Performs a check ("Dry Run") on the current role. """
    c = Check(ctx.obj.get('args'), {})
    c.execute
    util.sysexit(c.execute()[0])
