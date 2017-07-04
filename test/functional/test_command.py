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
        return False


@pytest.fixture
def driver_name(request):
    return request.param


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_check(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('check', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_converge(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('converge', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_create(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('dependency', 'docker', 'ansible-galaxy'),
        ('dependency', 'ec2', 'ansible-galaxy'),
        ('dependency', 'gce', 'ansible-galaxy'),
        ('dependency', 'lxc', 'ansible-galaxy'),
        ('dependency', 'lxd', 'ansible-galaxy'),
        ('dependency', 'openstack', 'ansible-galaxy'),
        ('dependency', 'vagrant', 'ansible-galaxy'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_dependency_ansible_galaxy(scenario_to_test, with_scenario,
                                           scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('dependency', **options)
    pytest.helpers.run_command(cmd)

    dependency_role = os.path.join('molecule', 'ansible-galaxy', '.molecule',
                                   'roles', 'timezone')
    assert os.path.isdir(dependency_role)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name', [
        ('dependency', 'docker', 'gilt'),
        ('dependency', 'ec2', 'gilt'),
        ('dependency', 'gce', 'gilt'),
        ('dependency', 'lxc', 'gilt'),
        ('dependency', 'lxd', 'gilt'),
        ('dependency', 'openstack', 'gilt'),
        ('dependency', 'vagrant', 'gilt'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_dependency_gilt(scenario_to_test, with_scenario,
                                 scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('dependency', **options)
    pytest.helpers.run_command(cmd)

    dependency_role = os.path.join('molecule', 'ansible-galaxy', '.molecule',
                                   'roles', 'timezone')
    assert os.path.isdir(dependency_role)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_destroy(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('destroy', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_destruct(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('destruct', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_idempotence(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.idempotence(scenario_name)


@pytest.mark.parametrize(
    'driver_name', [
        ('docker'),
        ('ec2'),
        ('gce'),
        ('lxc'),
        ('lxd'),
        ('openstack'),
        ('vagrant'),
    ],
    indirect=[
        'driver_name',
    ])
def test_command_init_role(temp_dir, driver_name, skip_test):
    pytest.helpers.init_role(temp_dir, driver_name)


@pytest.mark.parametrize(
    'driver_name', [
        ('docker'),
        ('ec2'),
        ('gce'),
        ('lxc'),
        ('lxd'),
        ('openstack'),
        ('vagrant'),
    ],
    indirect=[
        'driver_name',
    ])
def test_command_init_scenario(temp_dir, driver_name, skip_test):
    pytest.helpers.init_scenario(temp_dir, driver_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_lint(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('lint', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, expected',
    [
        ('driver/docker', 'docker', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Docker         Ansible             default          False      False
instance-1       Docker         Ansible             multi-node       False      False
instance-2       Docker         Ansible             multi-node       False      False
""".strip()),  # noqa
        ('driver/ec2', 'ec2', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Ec2            Ansible             default          False      False
instance-1       Ec2            Ansible             multi-node       False      False
instance-2       Ec2            Ansible             multi-node       False      False
""".strip()),  # noqa
        ('driver/gce', 'gce', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Gce            Ansible             default          False      False
instance-1       Gce            Ansible             multi-node       False      False
instance-2       Gce            Ansible             multi-node       False      False
""".strip()),  # noqa
        ('driver/lxc', 'lxc', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Lxc            Ansible             default          False      False
instance-1       Lxc            Ansible             multi-node       False      False
instance-2       Lxc            Ansible             multi-node       False      False
""".strip()),  # noqa
        ('driver/lxd', 'lxd', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Lxd            Ansible             default          False      False
instance-1       Lxd            Ansible             multi-node       False      False
instance-2       Lxd            Ansible             multi-node       False      False
""".strip()),  # noqa
        ('driver/openstack', 'openstack', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Openstack      Ansible             default          False      False
instance-1       Openstack      Ansible             multi-node       False      False
instance-2       Openstack      Ansible             multi-node       False      False
""".strip()),  # noqa
        ('driver/static', 'static', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
static-instance  Static         Ansible             docker           False      False
static-instance  Static         Ansible             ec2              False      False
static-instance  Static         Ansible             gce              False      False
static-instance  Static         Ansible             openstack        False      False
static-instance  Static         Ansible             vagrant          False      False
""".strip()),  # noqa
        ('driver/vagrant', 'vagrant', """
Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Vagrant        Ansible             default          False      False
instance-1       Vagrant        Ansible             multi-node       False      False
instance-2       Vagrant        Ansible             multi-node       False      False
""".strip()),  # noqa
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
    ])
def test_command_list(scenario_to_test, with_scenario, expected):
    pytest.helpers.list(expected)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, expected', [
        ('driver/docker', 'docker', """
instance    Docker  Ansible  default     False  False
instance-1  Docker  Ansible  multi-node  False  False
instance-2  Docker  Ansible  multi-node  False  False
""".strip()),
        ('driver/ec2', 'ec2', """
instance    Ec2  Ansible  default     False  False
instance-1  Ec2  Ansible  multi-node  False  False
instance-2  Ec2  Ansible  multi-node  False  False
""".strip()),
        ('driver/gce', 'gce', """
instance    Gce  Ansible  default     False  False
instance-1  Gce  Ansible  multi-node  False  False
instance-2  Gce  Ansible  multi-node  False  False
""".strip()),
        ('driver/lxc', 'lxc', """
instance    Lxc  Ansible  default     False  False
instance-1  Lxc  Ansible  multi-node  False  False
instance-2  Lxc  Ansible  multi-node  False  False
""".strip()),
        ('driver/lxd', 'lxd', """
instance    Lxd  Ansible  default     False  False
instance-1  Lxd  Ansible  multi-node  False  False
instance-2  Lxd  Ansible  multi-node  False  False
""".strip()),
        ('driver/openstack', 'openstack', """
instance    Openstack  Ansible  default     False  False
instance-1  Openstack  Ansible  multi-node  False  False
instance-2  Openstack  Ansible  multi-node  False  False
""".strip()),
        ('driver/static', 'static', """
static-instance-docker     Static  Ansible  docker     False  True
static-instance-ec2        Static  Ansible  ec2        False  True
static-instance-gce        Static  Ansible  gce        False  True
static-instance-openstack  Static  Ansible  openstack  False  True
static-instance-vagrant    Static  Ansible  vagrant    False  False
""".strip()),
        ('driver/vagrant', 'vagrant', """
instance    Vagrant  Ansible  default     False  False
instance-1  Vagrant  Ansible  multi-node  False  False
instance-2  Vagrant  Ansible  multi-node  False  False
""".strip()),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
    ])
def test_command_list_with_format_plain(scenario_to_test, with_scenario,
                                        expected):
    pytest.helpers.list_with_format_plain(expected)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, login_args, scenario_name',
    [
        ('driver/docker', 'docker', [[
            'instance',
            '.*instance.*',
        ]], 'default'),
        ('driver/docker', 'docker', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
        ('driver/ec2', 'ec2', [[
            'instance-1',
            '.*ip-.*',
        ], [
            'instance-2',
            '.*ip-.*',
        ]], 'multi-node'),
        ('driver/gce', 'gce', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
        ('driver/lxc', 'lxc', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
        ('driver/lxd', 'lxd', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
        ('driver/openstack', 'openstack', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
        ('driver/static', 'static', [[
            'static-instance-docker',
            '.*static-instance-docker.*',
        ]], 'docker'),
        ('driver/static', 'static', [[
            'static-instance-ec2',
            '.*ip-.*',
        ]], 'ec2'),
        ('driver/static', 'static', [[
            'static-instance-gce',
            '.*static-instance-gce.*',
        ]], 'gce'),
        ('driver/static', 'static', [[
            'static-instance-openstack',
            '.*static-instance-openstack.*',
        ]], 'openstack'),
        #  ('driver/static', 'static', [[
        #      'static-instance-vagrant',
        #      '.*static-instance-vagrant.*',
        #  ]], 'vagrant'),
        ('driver/vagrant', 'vagrant', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_login(scenario_to_test, with_scenario, login_args,
                       scenario_name):
    pytest.helpers.login(login_args, scenario_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_syntax(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('syntax', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', False),
        ('driver/ec2', 'ec2', False),
        ('driver/gce', 'gce', False),
        ('driver/lxc', 'lxc', False),
        ('driver/lxd', 'lxd', False),
        ('driver/openstack', 'openstack', False),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', False),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_test(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.test(scenario_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/docker', 'docker', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        ('driver/static', 'static', 'docker'),
        ('driver/static', 'static', 'ec2'),
        ('driver/static', 'static', 'gce'),
        ('driver/static', 'static', 'openstack'),
        #  ('driver/static', 'static', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_verify(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.verify(scenario_name)
