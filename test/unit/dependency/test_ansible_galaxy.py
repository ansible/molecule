#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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
import yaml

from molecule import config
from molecule.dependency import ansible_galaxy


@pytest.fixture()
def ansible_galaxy_instance(temp_files):
    confs = temp_files(fixtures=['molecule_vagrant_v1_config'])
    c = config.ConfigV1(configs=confs)
    c.config['dependency']['requirements_file'] = 'requirements.yml'

    return ansible_galaxy.AnsibleGalaxy(c.config)


def test_add_env_arg(ansible_galaxy_instance):
    ansible_galaxy_instance.add_env_arg('MOLECULE_1', 'test')

    assert 'test' == ansible_galaxy_instance._env['MOLECULE_1']


def test_check_meta_requirements(temp_dir, temp_files,
                                 ansible_galaxy_instance):
    requirements_file = temp_files(fixtures=['galaxy_meta_file'])[0]
    roles_directory = os.path.join(temp_dir, 'roles')

    expected_yaml = [{'role': 'molecule'}]
    expected_file = os.path.join(roles_directory, 'requirements.yml')
    assert expected_file == ansible_galaxy_instance.check_meta_requirements(
        requirements_file, roles_directory)
    with open(expected_file) as f:
        assert expected_yaml == yaml.load(f)


def test_execute(patched_ansible_galaxy, ansible_galaxy_instance):
    ansible_galaxy_instance.execute()

    patched_ansible_galaxy.assert_called_once()

    parts = str(ansible_galaxy_instance._galaxy).split()

    executable = sh.ansible_galaxy
    assert executable == parts[0]
    assert 'install' == parts[1]

    expected = [
        '--force', '--role-file=requirements.yml', '--roles-path=test/roles'
    ]
    assert expected == sorted(parts[2:])


def test_execute_overrides(patched_ansible_galaxy, ansible_galaxy_instance):
    ansible_galaxy_instance._config['dependency']['options'] = {
        'foo': 'bar',
        'force': False
    }
    ansible_galaxy_instance.execute()

    patched_ansible_galaxy.assert_called_once()

    parts = str(ansible_galaxy_instance._galaxy).split()
    expected = [
        '--foo=bar', '--role-file=requirements.yml', '--roles-path=test/roles'
    ]

    assert expected == sorted(parts[2:])


def test_execute_exits_with_return_code_and_logs(patched_print_error,
                                                 ansible_galaxy_instance):
    ansible_galaxy_instance._galaxy = sh.false.bake()
    with pytest.raises(SystemExit) as e:
        ansible_galaxy_instance.execute()

    assert 1 == e.value.code

    false_path = sh.which('false')
    msg = "\n\n  RAN: {}\n\n  STDOUT:\n\n\n  STDERR:\n".format(false_path)
    patched_print_error.assert_called_once_with(msg)
