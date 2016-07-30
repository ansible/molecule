#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import pytest

from molecule import ansible_playbook


@pytest.fixture()
def ansible():
    data = {
        'playbook': 'playbook.yml',
        'config_file': 'test.cfg',
        'limit': 'all',
        'verbose': 'vvvv',
        'diff': True,
        'host_key_checking': False,
        'raw_ssh_args': [
            '-o UserKnownHostsFile=/dev/null', '-o IdentitiesOnly=yes',
            '-o ControlMaster=auto', '-o ControlPersist=60s'
        ],
        'raw_env_vars': {
            'TEST_1': 'test_1'
        }
    }

    return ansible_playbook.AnsiblePlaybook(data)


def test_arg_loading(ansible):
    # string value set
    assert 'all' == ansible.cli['limit']

    # true value set
    assert ansible.cli['diff']

    # false values don't exist in arg dict at all
    assert ansible.cli.get('sudo_user') is None


def test_parse_arg_special_cases(ansible):
    # raw environment variables are set
    assert ansible.cli.get('raw_env_vars') is None
    assert 'test_1' == ansible.env['TEST_1']

    # raw_ssh_args set
    assert ansible.cli.get('raw_ssh_args') is None
    expected = ('-o UserKnownHostsFile=/dev/null -o IdentitiesOnly=yes '
                '-o ControlMaster=auto -o ControlPersist=60s')
    assert expected == ansible.env['ANSIBLE_SSH_ARGS']

    # host_key_checking gets set in environment as string 'false'
    assert ansible.cli.get('host_key_checking') is None
    assert 'false' == ansible.env['ANSIBLE_HOST_KEY_CHECKING']

    # config_file is set in environment
    assert ansible.cli.get('config_file') is None
    assert 'test.cfg' == ansible.env['ANSIBLE_CONFIG']

    # playbook is set as attribute
    assert ansible.cli.get('playbook') is None
    assert 'playbook.yml' == ansible.playbook

    # verbose is set in the right place
    assert ansible.cli.get('verbose') is None
    assert '-vvvv' in ansible.cli_pos


def test_add_cli_arg(ansible):
    # redefine a previously defined value
    ansible.add_cli_arg('limit', 'test')

    assert 'test' == ansible.cli['limit']

    # add a new value
    ansible.add_cli_arg('molecule_1', 'test')

    assert 'test' == ansible.cli['molecule_1']

    # values set as false shouldn't get added
    ansible.add_cli_arg('molecule_2', None)

    assert 'molecule_2' not in ansible.cli


def test_remove_cli_arg(ansible):
    ansible.remove_cli_arg('limit')

    assert 'limit' not in ansible.cli


def test_add_env_arg(ansible):
    # redefine a previously defined value
    ansible.add_env_arg('TEST_1', 'now')

    assert 'now' == ansible.env['TEST_1']

    # add a new value
    ansible.add_env_arg('MOLECULE_1', 'test')

    assert 'test' == ansible.env['MOLECULE_1']


def test_remove_env_arg(ansible):
    ansible.remove_env_arg('TEST_1')

    assert 'TEST_1' not in ansible.env
