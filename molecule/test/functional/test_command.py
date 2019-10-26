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

import os
from molecule.scenario import ephemeral_directory

import pytest
import sh


@pytest.fixture
def scenario_to_test(request):
    return request.param


@pytest.fixture
def scenario_name(request):
    try:
        return request.param
    except AttributeError:
        return None


@pytest.fixture
def driver_name(request):
    return request.param


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_check(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('check', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_cleanup(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('cleanup', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_converge(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_create(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.skip(
    reason="Disabled due to https://github.com/ansible/galaxy/issues/2030"
)
@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('dependency', 'docker', 'ansible-galaxy'),
        ('dependency', 'vagrant', 'ansible-galaxy'),
        ('dependency', 'podman', 'ansible-galaxy'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_dependency_ansible_galaxy(
    request, scenario_to_test, with_scenario, scenario_name
):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('dependency', **options)
    pytest.helpers.run_command(cmd)

    dependency_role = os.path.join(
        ephemeral_directory('molecule'),
        'dependency',
        'ansible-galaxy',
        'roles',
        'timezone',
    )
    assert os.path.isdir(dependency_role)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('dependency', 'docker', 'gilt'),
        ('dependency', 'vagrant', 'gilt'),
        ('dependency', 'podman', 'gilt'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_dependency_gilt(
    request, scenario_to_test, with_scenario, scenario_name
):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('dependency', **options)
    pytest.helpers.run_command(cmd)

    dependency_role = os.path.join(
        ephemeral_directory('molecule'), 'dependency', 'gilt', 'roles', 'timezone'
    )
    assert os.path.isdir(dependency_role)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('dependency', 'docker', 'shell'),
        ('dependency', 'vagrant', 'shell'),
        ('dependency', 'podman', 'shell'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_dependency_shell(
    request, scenario_to_test, with_scenario, scenario_name
):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('dependency', **options)
    pytest.helpers.run_command(cmd)

    dependency_role = os.path.join(
        ephemeral_directory('molecule'), 'dependency', 'shell', 'roles', 'timezone'
    )
    assert os.path.isdir(dependency_role)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_destroy(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('destroy', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_idempotence(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.idempotence(scenario_name)


@pytest.mark.parametrize(
    'driver_name', [('docker'), ('vagrant'), ('podman')], indirect=['driver_name']
)
def test_command_init_role(temp_dir, driver_name, skip_test):
    pytest.helpers.init_role(temp_dir, driver_name)


@pytest.mark.parametrize(
    'driver_name', [('docker'), ('vagrant'), ('podman')], indirect=['driver_name']
)
def test_command_init_scenario(temp_dir, driver_name, skip_test):
    pytest.helpers.init_scenario(temp_dir, driver_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_lint(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('lint', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, expected',
    [
        (
            'driver/docker',
            'docker',
            """
Instance Name    Driver Name    Provisioner Name    Scenario Name     Created    Converged
---------------  -------------  ------------------  ----------------  ---------  -----------
instance         docker         ansible             ansible-verifier  false      false
instance         docker         ansible             default           false      false
instance-1       docker         ansible             multi-node        false      false
instance-2       docker         ansible             multi-node        false      false
""".strip(),
        ),  # noqa
        (
            'driver/delegated',
            'delegated',
            """
Instance Name                 Driver Name    Provisioner Name    Scenario Name    Created    Converged
----------------------------  -------------  ------------------  ---------------  ---------  -----------
delegated-instance-docker     delegated      ansible             docker           unknown    true
""".strip(),
        ),  # noqa
        (
            'driver/vagrant',
            'vagrant',
            """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         vagrant        ansible             default          false      false
instance-1       vagrant        ansible             multi-node       false      false
instance-2       vagrant        ansible             multi-node       false      false
""".strip(),
        ),  # noqa
        (
            'driver/podman',
            'podman',
            """
Instance Name    Driver Name    Provisioner Name    Scenario Name     Created    Converged
---------------  -------------  ------------------  ----------------  ---------  -----------
instance         podman         ansible             ansible-verifier  false      false
instance         podman         ansible             default           false      false
instance-1       podman         ansible             multi-node        false      false
instance-2       podman         ansible             multi-node        false      false
""".strip(),
        ),  # noqa
    ],
    indirect=['scenario_to_test', 'driver_name'],
)
def test_command_list(scenario_to_test, with_scenario, expected):
    pytest.helpers.list(expected)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, expected',
    [
        (
            'driver/docker',
            'docker',
            """
instance    docker  ansible  ansible-verifier  false  false
instance    docker  ansible  default           false  false
instance-1  docker  ansible  multi-node        false  false
instance-2  docker  ansible  multi-node        false  false
""".strip(),
        ),
        (
            'driver/delegated',
            'delegated',
            """
delegated-instance-docker     delegated  ansible  docker     unknown  true
""".strip(),
        ),
        (
            'driver/vagrant',
            'vagrant',
            """
instance    vagrant  ansible  default     false  false
instance-1  vagrant  ansible  multi-node  false  false
instance-2  vagrant  ansible  multi-node  false  false
""".strip(),
        ),
        (
            'driver/podman',
            'podman',
            """
instance    podman  ansible  ansible-verifier  false  false
instance    podman  ansible  default           false  false
instance-1  podman  ansible  multi-node        false  false
instance-2  podman  ansible  multi-node        false  false
""".strip(),
        ),
    ],
    indirect=['scenario_to_test', 'driver_name'],
)
def test_command_list_with_format_plain(scenario_to_test, with_scenario, expected):
    pytest.helpers.list_with_format_plain(expected)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, login_args, scenario_name',
    [
        ('driver/docker', 'docker', [['instance', '.*instance.*']], 'default'),
        (
            'driver/docker',
            'docker',
            [['instance-1', '.*instance-1.*'], ['instance-2', '.*instance-2.*']],
            'multi-node',
        ),
        (
            'driver/delegated',
            'delegated',
            [['delegated-instance-docker', '.*delegated-instance-docker.*']],
            'docker',
        ),
        (
            'driver/vagrant',
            'vagrant',
            [['instance-1', '.*instance-1.*'], ['instance-2', '.*instance-2.*']],
            'multi-node',
        ),
        (
            'driver/podman',
            'podman',
            [['instance-1', '.*instance-1.*'], ['instance-2', '.*instance-2.*']],
            'multi-node',
        ),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_login(scenario_to_test, with_scenario, login_args, scenario_name):
    pytest.helpers.login(login_args, scenario_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_prepare(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}

    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake('prepare', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_side_effect(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('side-effect', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_syntax(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('syntax', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/docker', 'docker', 'ansible-verifier'),
        ('driver/docker', 'docker', 'multi-node'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', None),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_test(scenario_to_test, with_scenario, scenario_name, driver_name):
    pytest.helpers.test(driver_name, scenario_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/vagrant', 'vagrant', 'default'),
        ('driver/podman', 'podman', 'default'),
    ],
    indirect=['scenario_to_test', 'driver_name', 'scenario_name'],
)
def test_command_verify(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.verify(scenario_name)
