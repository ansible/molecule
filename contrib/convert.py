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

import argparse
import errno
import glob
import os
import shutil

from molecule import logger
from molecule import migrate
from molecule import util

LOG = logger.get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('old_molecule_file')
args = parser.parse_args()

old_molecule_file = args.old_molecule_file

if not os.path.isfile(old_molecule_file):
    msg = 'Unable to find {}. Exiting.'.format(old_molecule_file)
    util.sysexit_with_message(msg)

m = migrate.Migrate(old_molecule_file)
old_role_dir = os.path.join(os.path.dirname(old_molecule_file))
old_dot_molecule_dir = os.path.join(old_role_dir, '.molecule')
old_test_dir = os.path.join(old_role_dir, 'tests')
old_playbook = os.path.join(old_role_dir, 'playbook.yml')
molecule_dir = os.path.join(old_role_dir, 'molecule')
scenario_dir = os.path.join(molecule_dir, 'default')
test_dir = os.path.join(scenario_dir, 'tests')
molecule_file = os.path.join(scenario_dir, 'molecule.yml')

dirs = [
    molecule_dir,
    scenario_dir,
    test_dir,
]
for d in dirs:
    if not os.path.isdir(d):
        msg = 'Creating {}'.format(d)
        LOG.info(msg)
        os.mkdir(d)

with open(molecule_file, 'w') as stream:
    msg = 'Writing molecule.yml to {}'.format(molecule_file)
    LOG.info(msg)
    stream.write(m.dump())

for f in glob.glob(r'{}/test_*.py'.format(old_test_dir)):
    msg = 'Copying {} to {}'.format(f, test_dir)
    LOG.info(msg)
    shutil.copy(f, test_dir)

if os.path.isfile(old_playbook):
    msg = 'Copying {} to {}'.format(old_playbook, scenario_dir)
    LOG.info(msg)
    shutil.copy(old_playbook, scenario_dir)

files = [
    old_dot_molecule_dir,
    old_molecule_file,
    old_playbook,
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
