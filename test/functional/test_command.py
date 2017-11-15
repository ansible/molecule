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
        return None


@pytest.fixture
def driver_name(request):
    return request.param


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('dependency', 'azure', 'ansible-galaxy'),
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
        ('dependency', 'azure', 'gilt'),
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

    dependency_role = os.path.join('molecule', 'gilt', '.molecule', 'roles',
                                   'timezone')
    assert os.path.isdir(dependency_role)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('azure'),
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
        ('azure'),
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
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('driver/azure', 'azure', """

Instance Name    Driver Name    Provisioner Name    Scenario Name    Created    Converged
---------------  -------------  ------------------  ---------------  ---------  -----------
instance         Azure          Ansible             default          False      False
instance-1       Azure          Ansible             multi-node       False      False
instance-2       Azure          Ansible             multi-node       False      False
""".strip()),  # noqa
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
        ('driver/delegated', 'delegated', """
Instance Name                 Driver Name    Provisioner Name    Scenario Name    Created    Converged
----------------------------  -------------  ------------------  ---------------  ---------  -----------
delegated-instance-docker     Delegated      Ansible             docker           False      True
delegated-instance-ec2        Delegated      Ansible             ec2              False      True
delegated-instance-gce        Delegated      Ansible             gce              False      True
delegated-instance-openstack  Delegated      Ansible             openstack        False      True
delegated-instance-vagrant    Delegated      Ansible             vagrant          False      False
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
        ('driver/azure', 'azure', """
instance    Azure  Ansible  default     False  False
instance-1  Azure  Ansible  multi-node  False  False
instance-2  Azure  Ansible  multi-node  False  False
""".strip()),
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
        ('driver/delegated', 'delegated', """
delegated-instance-docker     Delegated  Ansible  docker     False  True
delegated-instance-ec2        Delegated  Ansible  ec2        False  True
delegated-instance-gce        Delegated  Ansible  gce        False  True
delegated-instance-openstack  Delegated  Ansible  openstack  False  True
delegated-instance-vagrant    Delegated  Ansible  vagrant    False  False
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
        ('driver/azure', 'azure', [[
            'instance',
            '.*instance.*',
        ]], 'default'),
        ('driver/azure', 'azure', [[
            'instance-1',
            '.*instance-1.*',
        ], [
            'instance-2',
            '.*instance-2.*',
        ]], 'multi-node'),
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
        ('driver/delegated', 'delegated', [[
            'delegated-instance-azure',
            '.*delegated-instance-azure.*',
        ]], 'azure'),
        ('driver/delegated', 'delegated', [[
            'delegated-instance-docker',
            '.*delegated-instance-docker.*',
        ]], 'docker'),
        ('driver/delegated', 'delegated', [[
            'delegated-instance-ec2',
            '.*ip-.*',
        ]], 'ec2'),
        ('driver/delegated', 'delegated', [[
            'delegated-instance-gce',
            '.*delegated-instance-gce.*',
        ]], 'gce'),
        ('driver/delegated', 'delegated', [[
            'delegated-instance-openstack',
            '.*delegated-instance-openstack.*',
        ]], 'openstack'),
        #  ('driver/delegated', 'delegated', [[
        #      'delegated-instance-vagrant',
        #      '.*delegated-instance-vagrant.*',
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
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_prepare(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}

    cmd = sh.molecule.bake('create', **options)
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake('prepare', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_side_effect(scenario_to_test, with_scenario, scenario_name):
    options = {'scenario_name': scenario_name}
    cmd = sh.molecule.bake('side-effect', **options)
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/ec2', 'ec2', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
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
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', None),
        ('driver/ec2', 'ec2', None),
        ('driver/gce', 'gce', None),
        ('driver/lxc', 'lxc', None),
        ('driver/lxd', 'lxd', None),
        ('driver/openstack', 'openstack', None),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
        ('driver/vagrant', 'vagrant', None),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_test(scenario_to_test, with_scenario, scenario_name,
                      driver_name):
    pytest.helpers.test(driver_name, scenario_name)


@pytest.mark.parametrize(
    'scenario_to_test, driver_name, scenario_name',
    [
        ('driver/azure', 'azure', 'default'),
        ('driver/docker', 'docker', 'default'),
        ('driver/gce', 'gce', 'default'),
        ('driver/lxc', 'lxc', 'default'),
        ('driver/lxd', 'lxd', 'default'),
        ('driver/openstack', 'openstack', 'default'),
        #  ('driver/delegated', 'delegated', 'azure'),
        ('driver/delegated', 'delegated', 'docker'),
        ('driver/delegated', 'delegated', 'ec2'),
        ('driver/delegated', 'delegated', 'gce'),
        ('driver/delegated', 'delegated', 'openstack'),
        #  ('driver/delegated', 'delegated', 'vagrant'),
        ('driver/vagrant', 'vagrant', 'default'),
    ],
    indirect=[
        'scenario_to_test',
        'driver_name',
        'scenario_name',
    ])
def test_command_verify(scenario_to_test, with_scenario, scenario_name):
    pytest.helpers.verify(scenario_name)
