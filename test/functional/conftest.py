#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#  Copyright (c) 2018 Red Hat, Inc.
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

import distutils.spawn
import os
import sys
from distutils.version import LooseVersion

import ansible
import pexpect
import pytest
import sh

from molecule import logger
from molecule import util

from ..conftest import change_dir_to

LOG = logger.get_logger(__name__)

IS_TRAVIS = os.getenv('TRAVIS') and os.getenv('CI')


@pytest.fixture
def with_scenario(request, scenario_to_test, driver_name, scenario_name,
                  skip_test):
    scenario_directory = os.path.join(
        os.path.dirname(util.abs_path(__file__)), os.path.pardir, 'scenarios',
        scenario_to_test)

    with change_dir_to(scenario_directory):
        yield
        if scenario_name:
            msg = 'CLEANUP: Destroying instances for all scenario(s)'
            LOG.out(msg)
            options = {
                'driver_name': driver_name,
                'all': True,
            }
            cmd = sh.molecule.bake('destroy', **options)
            pytest.helpers.run_command(cmd)


@pytest.fixture
def skip_test(request, driver_name):
    msg_tmpl = ("Ignoring '{}' tests for now" if driver_name == 'delegated'
                else "Skipped '{}' not supported")
    support_checks_map = {
        'azure': supports_azure,
        'docker': supports_docker,
        'ec2': supports_ec2,
        'gce': supports_gce,
        'lxc': supports_lxc,
        'lxd': supports_lxd,
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


@pytest.helpers.register
def idempotence(scenario_name):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('idempotence', **options)
    pytest.helpers.run_command(cmd)


@pytest.helpers.register
def init_role(temp_dir, driver_name):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')

    cmd = sh.molecule.bake('init', 'role', {
        'driver-name': driver_name,
        'role-name': 'test-init'
    })
    pytest.helpers.run_command(cmd)

    with change_dir_to(role_directory):
        options = {
            'all': True,
        }
        cmd = sh.molecule.bake('test', **options)
        pytest.helpers.run_command(cmd)


@pytest.helpers.register
def init_scenario(temp_dir, driver_name):
    # Create role
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    cmd = sh.molecule.bake('init', 'role', {
        'driver-name': driver_name,
        'role-name': 'test-init'
    })
    pytest.helpers.run_command(cmd)

    with change_dir_to(role_directory):
        # Create scenario
        molecule_directory = pytest.helpers.molecule_directory()
        scenario_directory = os.path.join(molecule_directory, 'test-scenario')

        options = {
            'scenario_name': 'test-scenario',
            'role_name': 'test-init',
        }
        cmd = sh.molecule.bake('init', 'scenario', **options)
        pytest.helpers.run_command(cmd)

        assert os.path.isdir(scenario_directory)

        options = {
            'scenario_name': 'test-scenario',
            'all': True,
        }
        cmd = sh.molecule.bake('test', **options)
        pytest.helpers.run_command(cmd)


@pytest.helpers.register
def list(x):
    cmd = sh.molecule.bake('list')
    out = pytest.helpers.run_command(cmd, log=False)
    out = out.stdout.decode('utf-8')
    out = util.strip_ansi_color(out)

    for l in x.splitlines():
        assert l in out


@pytest.helpers.register
def list_with_format_plain(x):
    cmd = sh.molecule.bake('list', {'format': 'plain'})
    out = pytest.helpers.run_command(cmd, log=False)
    out = out.stdout.decode('utf-8')
    out = util.strip_ansi_color(out)

    for l in x.splitlines():
        assert l in out


@pytest.helpers.register
def login(login_args, scenario_name='default'):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('destroy', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    for instance, regexp in login_args:
        if len(login_args) > 1:
            child_cmd = 'molecule login --host {} --scenario-name {}'.format(
                instance, scenario_name)
        else:
            child_cmd = 'molecule login --scenario-name {}'.format(
                scenario_name)
        child = pexpect.spawn(child_cmd)
        child.expect(regexp)
        # If the test returns and doesn't hang it succeeded.
        child.sendline('exit')


@pytest.helpers.register
def test(driver_name, scenario_name='default'):
    options = {
        'scenario_name': scenario_name,
        'all': True,
    }

    if driver_name == 'delegated':
        options = {
            'scenario_name': scenario_name,
        }

    cmd = sh.molecule.bake('test', **options)
    pytest.helpers.run_command(cmd)


@pytest.helpers.register
def verify(scenario_name='default'):
    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)

    options = {
        'scenario_name': scenario_name,
    }
    cmd = sh.molecule.bake('verify', **options)
    pytest.helpers.run_command(cmd)


def get_docker_executable():
    return distutils.spawn.find_executable('docker')


def get_lxc_executable():
    return distutils.spawn.find_executable('lxc-start')


def get_lxd_executable():
    return distutils.spawn.find_executable('lxd')


def get_vagrant_executable():
    return distutils.spawn.find_executable('vagrant')


def get_virtualbox_executable():
    return distutils.spawn.find_executable('VBoxManage')


@pytest.helpers.register
def supports_docker():
    return get_docker_executable()


@pytest.helpers.register
def supports_lxc():
    # noqa: E501 # FIXME: Travis CI
    # noqa: E501 # This fixes most of the errors:
    # noqa: E501 # $ mkdir -p ~/.config/lxc
    # noqa: E501 # $ echo "lxc.id_map = u 0 100000 65536" > ~/.config/lxc/default.conf
    # noqa: E501 # $ echo "lxc.id_map = g 0 100000 65536" >> ~/.config/lxc/default.conf
    # noqa: E501 # $ echo "lxc.network.type = veth" >> ~/.config/lxc/default.conf
    # noqa: E501 # $ echo "lxc.network.link = lxcbr0" >> ~/.config/lxc/default.conf
    # noqa: E501 # $ echo "$USER veth lxcbr0 2" | sudo tee -a /etc/lxc/lxc-usernet
    # noqa: E501 # travis veth lxcbr0 2
    # noqa: E501 # But there's still one left:
    # noqa: E501 # $ cat ~/lxc-instance.log
    # noqa: E501 # lxc-create 1542112494.884 INFO     lxc_utils - utils.c:get_rundir:229 - XDG_RUNTIME_DIR isn't set in the environment.
    # noqa: E501 # lxc-create 1542112494.884 WARN     lxc_log - log.c:lxc_log_init:331 - lxc_log_init called with log already initialized
    # noqa: E501 # lxc-create 1542112494.884 INFO     lxc_confile - confile.c:config_idmap:1385 - read uid map: type u nsid 0 hostid 100000 range 65536
    # noqa: E501 # lxc-create 1542112494.884 INFO     lxc_confile - confile.c:config_idmap:1385 - read uid map: type g nsid 0 hostid 100000 range 65536
    # noqa: E501 # lxc-create 1542112494.887 ERROR    lxc_container - lxccontainer.c:do_create_container_dir:767 - Failed to chown container dir
    # noqa: E501 # lxc-create 1542112494.887 ERROR    lxc_create_ui - lxc_create.c:main:274 - Error creating container instance
    return not IS_TRAVIS and get_lxc_executable()


@pytest.helpers.register
def supports_lxd():
    # FIXME: Travis CI
    return not IS_TRAVIS and get_lxd_executable()


@pytest.helpers.register
def supports_vagrant_virtualbox():
    return (get_vagrant_executable() or get_virtualbox_executable())


@pytest.helpers.register
def demands_delegated():
    return pytest.config.getoption('--delegated')


@pytest.helpers.register
def supports_azure():
    # FIXME: come up with an actual check
    return not IS_TRAVIS  # FIXME: Travis CI


@pytest.helpers.register
def supports_ec2():
    # FIXME: come up with an actual check
    return not IS_TRAVIS  # FIXME: Travis CI


@pytest.helpers.register
def supports_gce():
    # FIXME: come up with an actual check
    return not IS_TRAVIS  # FIXME: Travis CI


@pytest.helpers.register
def supports_openstack():
    # FIXME: come up with an actual check
    return not IS_TRAVIS  # FIXME: Travis CI


@pytest.helpers.register
def has_inspec():
    return distutils.spawn.find_executable('inspec')


@pytest.helpers.register
def has_rubocop():
    return distutils.spawn.find_executable('rubocop')


needs_inspec = pytest.mark.skipif(
    not has_inspec(),
    reason='Needs inspec to be pre-installed and available in $PATH')

needs_rubocop = pytest.mark.skipif(
    not has_rubocop(),
    reason='Needs rubocop to be pre-installed and available in $PATH')


@pytest.helpers.register
def is_supported_ansible_python_combo():
    ansible_below_25 = LooseVersion(ansible.__version__) < LooseVersion('2.5')
    max_py = (3, 6) if ansible_below_25 else (3, 7)
    return sys.version_info[:2] <= max_py


skip_unsupported_matrix = pytest.mark.skipif(
    not is_supported_ansible_python_combo(),
    reason='Current combination of Ansible and Python is not supported')
