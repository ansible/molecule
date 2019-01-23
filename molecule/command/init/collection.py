#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#  Copyright (c) 2019 Ansible Project
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

from molecule import logger
from molecule import util
from molecule.command.init import base

LOG = logger.get_logger(__name__)


class Collection(base.Base):
    """
    .. program:: molecule init collection --namespace foo --name bar

    .. option:: molecule init collection --namespace foo --name bar

        Initialize a new collection.
    """

    def __init__(self, command_args):
        self._command_args = command_args

    def execute(self):
        collection_namespace = self._command_args['collection_namespace']
        collection_name = self._command_args['collection_name']
        collection_directory = os.getcwd()
        collection_path = collection_namespace + '.' + collection_name
        msg = 'Initializing new collection {}...'.format(collection_path)
        LOG.info(msg)

        if os.path.isdir(collection_path):
            msg = ('The directory {} exists. '
                   'Cannot create new collection.').format(collection_path)
            util.sysexit_with_message(msg)

        self._process_templates('collection', self._command_args,
                                collection_directory)
        msg = 'Initialized colletion in {} successfully.'.format(
            collection_path)

        # TODO create the default scenario

        LOG.success(msg)


@click.command()
@click.pass_context
@click.option(
    '--namespace',
    '-n',
    required=True,
    help='Namespace of the collection.')
@click.option(
    '--name', '-c', required=True, help='Name of the collection.')
def collection(ctx, namespace, name):  # pragma: no cover
    """Initialize a new collection for use with Molecule."""
    command_args = {
        'collection_namespace': namespace,
        'collection_name': name,
    }

    col = Collection(command_args)
    col.execute()
