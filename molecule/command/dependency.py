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

from molecule import util
from molecule.command import base
from molecule.dependency import ansible_galaxy
from molecule.dependency import shell


class Dependency(base.Base):
    def execute(self, exit=True):
        """
        Execute the actions that should run prior to a converge and return a
        tuple.

        :param exit: (Unused) Provided to complete method signature.
        :return: Return a tuple provided by :meth:`.AnsiblePlaybook.execute`.
        """
        debug = self.args.get('debug')
        if self.molecule.state.installed_deps:
            return (None, None)
        dependency_name = self.molecule.dependency
        if dependency_name == 'galaxy':
            dd = self.molecule.config.config.get('dependency')
            if dd.get('requirements_file'):
                msg = "Downloading dependencies with '{}'...".format(
                    dependency_name)
                util.print_info(msg)
                g = ansible_galaxy.AnsibleGalaxy(
                    self.molecule.config.config, debug=debug)
                g.execute()
                self.molecule.state.change_state('installed_deps', True)
        elif dependency_name == 'shell':
            dd = self.molecule.config.config.get('dependency')
            if dd.get('command'):
                msg = "Downloading dependencies with '{}'...".format(
                    dependency_name)
                util.print_info(msg)
                s = shell.Shell(self.molecule.config.config, debug=debug)
                s.execute()
                self.molecule.state.change_state('installed_deps', True)

        return (None, None)


@click.command()
@click.pass_context
def dependency(ctx):  # pragma: no cover
    """ Perform dependent actions on the current role. """
    d = Dependency(ctx.obj.get('args'), {})
    d.execute
    util.sysexit(d.execute()[0])
