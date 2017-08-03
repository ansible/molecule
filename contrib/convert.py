#!/usr/bin/env python
#
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

import errno
import glob
import os
import shutil

import click
import sh

from molecule import config
from molecule import logger
from molecule import migrate
from molecule import scenario
from molecule import util

LOG = logger.get_logger(__name__)


class Convert(object):
    def __init__(self, old_molecule_file, driver_name):
        self._old_molecule_file = old_molecule_file

        if not os.path.isfile(old_molecule_file):
            msg = 'Unable to find {}. Exiting.'.format(old_molecule_file)
            util.sysexit_with_message(msg)

        self._m = migrate.Migrate(old_molecule_file)
        self._old_role_dir = os.path.join(os.path.dirname(old_molecule_file))
        self._old_dot_molecule_dir = scenario.ephemeral_directory(
            self._old_role_dir)
        self._old_test_dir = os.path.join(self._old_role_dir, 'tests')
        self._old_playbook = os.path.join(self._old_role_dir, 'playbook.yml')
        self._molecule_dir = config.molecule_directory(self._old_role_dir)
        self._scenario_dir = os.path.join(self._molecule_dir, 'default')
        self._test_dir = os.path.join(self._scenario_dir, 'tests')
        self._molecule_file = config.molecule_file(self._scenario_dir)

        self._role_name = os.path.basename(
            os.path.normpath(self._old_role_dir))

    def migrate(self):
        self._create_scenario()
        self._create_new_molecule_file()
        self._copy_old_files()
        self._cleanup_old_files()

    def _create_scenario(self):
        options = {
            'role_name': self._role_name,
            'scenario_name': 'default',
            'driver_name': 'vagrant',
        }
        cmd = sh.molecule.bake(
            'init', 'scenario', _cwd=self._old_role_dir, **options)
        util.run_command(cmd)

    def _create_new_molecule_file(self):
        with open(self._molecule_file, 'w') as stream:
            msg = 'Writing molecule.yml to {}'.format(self._molecule_file)
            LOG.info(msg)
            stream.write(self._m.dump())

    def _copy_old_files(self):
        for f in glob.glob(r'{}/test_*.py'.format(self._old_test_dir)):
            msg = 'Copying {} to {}'.format(f, self._test_dir)
            LOG.info(msg)
            shutil.copy(f, self._test_dir)

        if os.path.isfile(self._old_playbook):
            msg = 'Copying {} to {}'.format(self._old_playbook,
                                            self._scenario_dir)
            LOG.info(msg)
            shutil.copy(self._old_playbook, self._scenario_dir)

    def _cleanup_old_files(self):
        files = [
            self._old_dot_molecule_dir,
            self._old_molecule_file,
            self._old_playbook,
        ]
        for f in files:
            if os.path.exists(f):
                msg = 'Deleting {}'.format(f)
                LOG.warn(msg)
                try:
                    shutil.rmtree(f)
                except OSError as exc:
                    if exc.errno == errno.ENOTDIR:
                        os.remove(f)
                    else:
                        raise


@click.command()
@click.argument('old_molecule_file', required=True)
@click.option(
    '--driver-name',
    '-d',
    type=click.Choice(['vagrant']),
    default='vagrant',
    help='Name of driver to migrate. (vagrant)')
def main(old_molecule_file, driver_name):  # pragma: no cover
    """ Migrate a Molecule v1 role to the v2 format. """

    c = Convert(old_molecule_file, driver_name)
    c.migrate()


if __name__ == '__main__':
    main()
