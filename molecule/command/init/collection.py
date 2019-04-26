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
import spdx

from molecule import config
from molecule import logger
from molecule import util
from molecule.command import base as command_base
from molecule.command.init import base

LOG = logger.get_logger(__name__)


def _get_spdx_license_ids():
    return set(l['id'] for l in spdx.licenses())


def _is_valid_spdx_id(spdx_id):
    return spdx_id in _get_spdx_license_ids()


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
        collection_directory = self._command_args['collection_directory']
        if collection_directory is None:
            collection_directory = os.getcwd()
        (  # Hack with specifying a role_name var allows us to reuse the
           # existing template structures previously created for roles.
           # FIXME: Improve this by renaming everything to more generic
           # FIXME: variable type.
            self._command_args['role_name']
        ) = collection_path = (
            '{space}.{name}'.
            format(
                space=collection_namespace, name=collection_name,
            )
        )
        msg = 'Initializing new collection {}...'.format(collection_path)
        LOG.info(msg)

        if os.path.isdir(collection_path):
            msg = ('The directory {} exists. '
                   'Cannot create new collection.').format(collection_path)
            util.sysexit_with_message(msg)

        template_directory = self._command_args.get('template', 'collection')

        self._process_templates(template_directory, self._command_args,
                                collection_directory)

        scenario_base_directory = os.path.join(
            collection_directory,
            collection_path,
            # collection_name,
        )
        templates = [
            'scenario/driver/{driver_name}'.format(**self._command_args),
            'scenario/verifier/{verifier_name}'.format(**self._command_args),
        ]
        for template in templates:
            self._process_templates(template, self._command_args,
                                    scenario_base_directory)
        self._process_templates(
            'molecule', self._command_args, collection_directory,
        )

        msg = 'Initialized colletion in {} successfully.'.format(
            collection_path)

        LOG.success(msg)


@click.command()
@click.pass_context
@click.option(
    '--dependency-name',
    type=click.Choice(['galaxy']),
    default='galaxy',
    help='Name of dependency to initialize. (galaxy)')
@click.option(
    '--driver-name',
    '-d',
    type=click.Choice(config.molecule_drivers()),
    default='docker',
    help='Name of driver to initialize. (docker)')
@click.option(
    '--lint-name',
    type=click.Choice(['yamllint']),
    default='yamllint',
    help='Name of lint to initialize. (yamllint)')
@click.option(
    '--collection-namespace', '-n', required=True,
    help='Namespace of the collection.',
)
@click.option(
    '--collection-name', '-c', required=True,
    help='Name of the collection.',
)
@click.option(
    '--directory',
    '-d',
    required=False,
    help='Directory path for the new collection.')
@click.option(
    '--provisioner-name',
    type=click.Choice(['ansible']),
    default='ansible',
    help='Name of provisioner to initialize. (ansible)')
@click.option(
    '--template',
    '-t',
    type=click.Path(
        exists=True, dir_okay=True, readable=True, resolve_path=True),
    help='Path to a cookiecutter custom template to initialize the '
    'collection. The upstream molecule folder will be added to '
    'this template.',
)
@click.option(
    '--verifier-name',
    type=click.Choice(config.molecule_verifiers()),
    default='testinfra',
    help='Name of verifier to initialize. (testinfra)')
def collection(
        ctx,  # pylint: disable=unused-argument
        dependency_name,
        directory, driver_name,
        collection_namespace, collection_name,
        lint_name, provisioner_name,
        template, verifier_name,
):  # pragma: no cover
    """Initialize a new collection for use with Molecule."""
    command_args = {
        'collection_namespace': collection_namespace,
        'collection_name': collection_name,
        'collection_directory': directory,
        'dependency_name': dependency_name,
        'driver_name': driver_name,
        'lint_name': lint_name,
        'provisioner_name': provisioner_name,
        'scenario_name': command_base.MOLECULE_DEFAULT_SCENARIO_NAME,
        'subcommand': __name__,
        'verifier_name': verifier_name,
    }

    verifier_linter_map = {
        'inspec': 'rubocop',
        'goss': 'yamllint',
        'ansible': 'ansible-lint',
    }
    verifier_linter = verifier_linter_map.get(verifier_name, None)
    if verifier_linter is not None:
        command_args['verifier_lint_name'] = verifier_linter

    if template is not None:
        command_args['template'] = template

    Collection(command_args).execute()
