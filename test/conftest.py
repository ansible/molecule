#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

import contextlib
import os
import random
import string
import tempfile

import pytest

from molecule import config
from molecule import logger
from molecule import util

LOG = logger.get_logger(__name__)

pytest_plugins = ['helpers_namespace']


@pytest.helpers.register
def run_command(cmd, env=os.environ, log=True):
    if log:
        cmd = _rebake_command(cmd, env)

    return util.run_command(cmd)


def _rebake_command(cmd, env, out=LOG.out, err=LOG.error):
    return cmd.bake(_env=env, _out=out, _err=err)


@pytest.fixture
def random_string(l=5):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(l))


@contextlib.contextmanager
def change_dir_to(dir_name):
    cwd = os.getcwd()
    os.chdir(dir_name)
    yield
    os.chdir(cwd)


@pytest.fixture
def temp_dir(tmpdir, random_string, request):
    directory = tmpdir.mkdir(random_string)

    with change_dir_to(directory.strpath):
        yield directory


@pytest.helpers.register
def molecule_project_directory():
    return os.getcwd()


@pytest.helpers.register
def molecule_directory():
    return config.molecule_directory(molecule_project_directory())


@pytest.helpers.register
def molecule_scenario_directory():
    return os.path.join(molecule_directory(), 'default')


@pytest.helpers.register
def molecule_file():
    return get_molecule_file(molecule_scenario_directory())


@pytest.helpers.register
def get_molecule_file(path):
    return config.molecule_file(path)


@pytest.helpers.register
def molecule_ephemeral_directory():
    project_directory = 'test-project'
    scenario_name = 'test-instance'

    return os.path.join(tempfile.gettempdir(), 'molecule', project_directory,
                        scenario_name)


def pytest_addoption(parser):
    parser.addoption(
        '--delegated', action='store_true', help='Run delegated driver tests.')


def pytest_collection_modifyitems(items):
    marker = pytest.config.getoption('-m')
    is_sharded = False
    shard_id = 0
    shards_num = 0
    if not marker.startswith('shard_'):
        return
    shard_id, _, shards_num = marker[6:].partition('_of_')
    if shards_num:
        shard_id = int(shard_id)
        shards_num = int(shards_num)
        is_sharded = True
    else:
        raise ValueError('shard_{}_of_{} marker is invalid')
    if not is_sharded:
        return
    if not (0 < shard_id <= shards_num):
        raise ValueError(
            'shard_id must be greater than 0 and not bigger than shards_num')
    for test_counter, item in enumerate(items):
        cur_shard_id = test_counter % shards_num + 1
        marker = getattr(pytest.mark, 'shard_{}_of_{}'.format(
            cur_shard_id,
            shards_num,
        ))
        item.add_marker(marker)
    del marker
    print('Running sharded test group #{} out of {}'.format(
        shard_id, shards_num))


@pytest.fixture(autouse=True)
def reset_pytest_vars(monkeypatch):
    """Make PYTEST_* env vars inaccessible to subprocesses."""
    for var_name in tuple(os.environ):
        if var_name.startswith('PYTEST_'):
            monkeypatch.delenv(var_name, raising=False)
