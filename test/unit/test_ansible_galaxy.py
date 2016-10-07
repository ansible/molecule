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

import re

import pytest
import sh

from molecule import ansible_galaxy
from molecule import config


@pytest.fixture()
def ansible_galaxy_instance(temp_files):
    confs = temp_files(fixtures=['molecule_vagrant_config'])
    c = config.Config(configs=confs)
    c.config['ansible']['requirements_file'] = 'requirements.yml'

    return ansible_galaxy.AnsibleGalaxy(c.config)


def test_add_env_arg(ansible_galaxy_instance):
    ansible_galaxy_instance.add_env_arg('MOLECULE_1', 'test')

    assert 'test' == ansible_galaxy_instance.env['MOLECULE_1']


def test_install(patched_ansible_galaxy, ansible_galaxy_instance):
    ansible_galaxy_instance.install()

    patched_ansible_galaxy.assert_called_once()

    # NOTE(retr0h): The following is a somewhat gross test, but need to
    # handle **kwargs expansion being unordered.
    parts = str(ansible_galaxy_instance._galaxy).split()
    expected = ['--force', '--role-file=requirements.yml',
                '--roles-path=test/roles']

    assert re.search(r'ansible-galaxy', parts[0])
    assert 'install' == parts[1]
    assert expected == sorted(parts[2:])


def test_install_overrides(patched_ansible_galaxy, ansible_galaxy_instance):
    ansible_galaxy_instance._config['ansible']['galaxy'] = {'foo': 'bar',
                                                            'force': False}
    ansible_galaxy_instance.install()

    patched_ansible_galaxy.assert_called_once

    parts = str(ansible_galaxy_instance._galaxy).split()
    expected = ['--foo=bar', '--role-file=requirements.yml',
                '--roles-path=test/roles']

    assert expected == sorted(parts[2:])


def test_execute(mocker, ansible_galaxy_instance):
    mocker.patch('sh.ansible_galaxy')
    result = ansible_galaxy_instance.execute()

    assert isinstance(result, mocker.Mock)


def test_execute_exits_with_return_code_and_logs(patched_logger_error,
                                                 ansible_galaxy_instance):
    ansible_galaxy_instance._galaxy = sh.false.bake()
    with pytest.raises(SystemExit) as e:
        ansible_galaxy_instance.execute()

    assert 1 == e.value.code

    msg = "ERROR: \n\n  RAN: '/usr/bin/false'\n\n  STDOUT:\n\n\n  STDERR:\n"
    patched_logger_error.assert_called_once_with(msg)
