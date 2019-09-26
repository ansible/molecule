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
import distutils
import os
import random
import string

import pytest

from molecule import config
from molecule import logger
from molecule import util
from molecule.driver.docker import Docker
from molecule.scenario import ephemeral_directory

LOG = logger.get_logger(__name__)


@util.lru_cache()
def has_docker():
    try:
        Docker().sanity_checks()
    except:
        return False
    return True


@pytest.helpers.register
def run_command(cmd, env=os.environ, log=True):
    if log:
        cmd = _rebake_command(cmd, env)

    # Never let sh truncate exceptions in testing
    cmd = cmd.bake(_truncate_exc=False)

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


@pytest.fixture
def resources_folder_path():
    resources_folder_path = os.path.join(os.path.dirname(__file__), 'resources')
    return resources_folder_path


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
def molecule_ephemeral_directory(_fixture_uuid):
    project_directory = 'test-project-{}'.format(_fixture_uuid)
    scenario_name = 'test-instance'

    return ephemeral_directory(
        os.path.join('molecule_test', project_directory, scenario_name)
    )


def pytest_addoption(parser):
    parser.addoption(
        '--delegated', action='store_true', help='Run delegated driver tests.'
    )


def pytest_collection_modifyitems(items, config):

    marker = config.getoption('-m')
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
            'shard_id must be greater than 0 and not bigger than shards_num'
        )
    for test_counter, item in enumerate(items):
        cur_shard_id = test_counter % shards_num + 1
        marker = getattr(pytest.mark, 'shard_{}_of_{}'.format(cur_shard_id, shards_num))
        item.add_marker(marker)
    del marker
    print('Running sharded test group #{} out of {}'.format(shard_id, shards_num))


@pytest.fixture(autouse=True)
def reset_pytest_vars(monkeypatch):
    """Make PYTEST_* env vars inaccessible to subprocesses."""
    for var_name in tuple(os.environ):
        if var_name.startswith('PYTEST_'):
            monkeypatch.delenv(var_name, raising=False)


@pytest.fixture
def patched_docker_sanity_check(mocker):
    return mocker.patch(
        'molecule.driver.docker.Docker.sanity_checks', return_value=True
    )


@pytest.fixture
def skip_test(request, driver_name):
    msg_tmpl = (
        "Ignoring '{}' tests for now"
        if driver_name == 'delegated'
        else "Skipped '{}' not supported"
    )
    support_checks_map = {
        'digitalocean': supports_digitalocean,
        'docker': supports_docker,
        'ec2': supports_ec2,
        'gce': supports_gce,
        'hetznercloud': lambda: at_least_ansible_28() and supports_hetznercloud(),
        'linode': lambda: at_least_ansible_28() and supports_linode(),
        'openstack': supports_openstack,
        'vagrant': supports_vagrant_virtualbox,
        'delegated': demands_delegated,
    }
    try:
        check_func = support_checks_map[driver_name]
        if not check_func():
            pytest.skip(msg_tmpl.format(driver_name))
    except KeyError:
        pass


def get_docker_executable():
    return distutils.spawn.find_executable('docker')


def get_vagrant_executable():
    return distutils.spawn.find_executable('vagrant')


def get_virtualbox_executable():
    return distutils.spawn.find_executable('VBoxManage')


@pytest.helpers.register
def supports_docker():
    return get_docker_executable()


@pytest.helpers.register
def supports_digitalocean():
    try:
        # ansible >=2.8
        # The _digital_ocean module is deprecated, and will be removed in
        # ansible 2.12. This is a temporary fix, and should be addressed
        # based on decisions made in the related github issue:
        # https://github.com/ansible/molecule/issues/2054
        from ansible.modules.cloud.digital_ocean._digital_ocean import HAS_DOPY
    except ImportError:
        # ansible <2.8
        from ansible.modules.cloud.digital_ocean.digital_ocean import HAS_DOPY

    env_vars = ('DO_API_KEY',)

    return _env_vars_exposed(env_vars) and HAS_DOPY


@pytest.helpers.register
def supports_ec2():
    from ansible.module_utils.ec2 import HAS_BOTO3

    env_vars = ('AWS_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')

    return _env_vars_exposed(env_vars) and HAS_BOTO3


@pytest.helpers.register
def supports_gce():
    from ansible.module_utils.gcp import HAS_GOOGLE_AUTH

    env_vars = ('GCE_SERVICE_ACCOUNT_EMAIL', 'GCE_CREDENTIALS_FILE', 'GCE_PROJECT_ID')

    return _env_vars_exposed(env_vars) and HAS_GOOGLE_AUTH


@pytest.helpers.register
def supports_hetznercloud():
    pytest.importorskip('hcloud')

    env_vars = ('HCLOUD_TOKEN',)

    return _env_vars_exposed(env_vars)


@pytest.helpers.register
def supports_linode():
    from ansible.modules.cloud.linode.linode_v4 import HAS_LINODE_DEPENDENCY

    env_vars = ('LINODE_ACCESS_TOKEN',)

    return _env_vars_exposed(env_vars) and HAS_LINODE_DEPENDENCY


@pytest.helpers.register
def supports_vagrant_virtualbox():
    return get_vagrant_executable() or get_virtualbox_executable()


@pytest.helpers.register
def supports_openstack():
    pytest.importorskip('shade')  # Ansible provides no import

    env_vars = (
        'OS_AUTH_URL',
        'OS_PASSWORD',
        'OS_REGION_NAME',
        'OS_USERNAME',
        'OS_TENANT_NAME',
    )

    return _env_vars_exposed(env_vars)


@pytest.helpers.register
def demands_delegated():
    return pytest.config.getoption('--delegated')


def _env_vars_exposed(env_vars, env=os.environ):
    """Check if environment variables are exposed and populated."""
    for env_var in env_vars:
        if env_var not in os.environ:
            return False
        return os.environ[env_var] != ''