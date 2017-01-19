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

import click

import molecule
from molecule import command


def main():
    """ Molecule aids in the development, and testing of Ansible roles. """
    cli(obj={})


@click.group()
@click.option(
    '--debug/--no-debug',
    default=False,
    help='Enable or disable debug mode. Default is disabled.')
@click.version_option(version=molecule.__version__)
@click.pass_context
def cli(ctx, debug):  # pragma: no cover
    ctx.obj['args'] = {}
    ctx.obj['args']['debug'] = debug


cli.add_command(command.check.check)
cli.add_command(command.converge.converge)
cli.add_command(command.create.create)
cli.add_command(command.dependency.dependency)
cli.add_command(command.destroy.destroy)
cli.add_command(command.idempotence.idempotence)
cli.add_command(command.init.init)
cli.add_command(command.lint.lint)
cli.add_command(command.list.list)
cli.add_command(command.login.login)
cli.add_command(command.syntax.syntax)
cli.add_command(command.test.test)
cli.add_command(command.verify.verify)
