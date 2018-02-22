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

import click
import cookiecutter
import cookiecutter.main

from molecule import logger
from molecule import util
from molecule.command.init import base

LOG = logger.get_logger(__name__)


class Template(base.Base):
    """
    Initialize a new role from a Cookiecutter URL:

    $ molecule init template --url https://example.com/user/cookiecutter-repo
    """

    def __init__(self, command_args):
        self._command_args = command_args

    def execute(self):
        """
        Execute the actions necessary to perform a `molecule init template` and
        returns None.

        :return: None
        """

        role_name = self._command_args['role_name']
        url = self._command_args['url']
        no_input = self._command_args['no_input']
        role_directory = os.getcwd()
        msg = 'Initializing new role {}...'.format(role_name)
        LOG.info(msg)

        if os.path.isdir(role_name):
            msg = ('The directory {} exists. '
                   'Cannot create new role.').format(role_name)
            util.sysexit_with_message(msg)

        cookiecutter.main.cookiecutter(
            url,
            extra_context=self._command_args,
            no_input=no_input, )

        role_directory = os.path.join(os.getcwd(), role_name)
        msg = 'Initialized role in {} successfully.'.format(role_directory)
        LOG.success(msg)


@click.command()
@click.pass_context
@click.option(
    '--url',
    required=True,
    help='URL to the Cookiecutter templates repository.')
@click.option(
    '--no-input/--input',
    default=False,
    help=('Do not prompt for parameters and only use cookiecutter.json for '
          'content. (false)'))
@click.option(
    '--role-name',
    '-r',
    default='role_name',
    help='Name of the role to create.')
def template(ctx, url, no_input, role_name):  # pragma: no cover
    """ Initialize a new role from a Cookiecutter URL. """
    command_args = {
        'role_name': role_name,
        'subcommand': __name__,
        'url': url,
        'no_input': no_input,
    }

    t = Template(command_args)
    t.execute()
