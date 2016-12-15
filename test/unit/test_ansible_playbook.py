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

import pytest
import re
import sh

from molecule import ansible_playbook


@pytest.fixture()
def ansible_playbook_instance(ansible_v1_section_data):
    return ansible_playbook.AnsiblePlaybook(ansible_v1_section_data['ansible'],
                                            {})


def test_init_arg_loading_string(ansible_playbook_instance):
    assert 'all' == ansible_playbook_instance._cli.get('limit')


def test_init_arg_loading_bool_true(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('diff')


def test_init_arg_loading_bool_false_not_added(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('sudo_user') is None


def test_init_connection_params(ansible_v1_section_data,
                                ansible_playbook_instance):
    connection_params = {'foo': 'bar'}
    a = ansible_playbook.AnsiblePlaybook(ansible_v1_section_data['ansible'],
                                         connection_params)
    assert 'bar' == a._cli.get('foo')


def test_parse_arg_raw_env(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('raw_env_vars') is None
    assert 'bar' == ansible_playbook_instance.env.get('FOO')


def test_parse_arg_host_key_checking(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('host_key_checking') is None
    assert 'false' == ansible_playbook_instance.env.get(
        'ANSIBLE_HOST_KEY_CHECKING')


def test_parse_arg_raw_ssh_args(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('raw_ssh_args') is None
    expected = ('-o UserKnownHostsFile=/dev/null -o IdentitiesOnly=yes '
                '-o ControlMaster=auto -o ControlPersist=60s')
    assert expected == ansible_playbook_instance.env.get('ANSIBLE_SSH_ARGS')


def test_parse_arg_config_file(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('config_file') is None
    assert 'config_file' == ansible_playbook_instance.env.get('ANSIBLE_CONFIG')


def test_parse_arg_playbook(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('playbook') is None
    assert 'playbook_data.yml' == pytest.helpers.os_split(
        ansible_playbook_instance._playbook)[-1]


def test_parse_arg_host_vars(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('host_vars') is None


def test_parse_arg_group_vars(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('group_vars') is None


def test_parse_arg_verbose(ansible_playbook_instance):
    assert ansible_playbook_instance._cli.get('verbose') is None
    assert '-vvvv' in ansible_playbook_instance._cli_pos


def test_add_cli_arg(ansible_playbook_instance):
    ansible_playbook_instance.add_cli_arg('foo', 'bar')

    assert 'bar' == ansible_playbook_instance._cli.get('foo')


def test_add_cli_arg_redefine_existing(ansible_playbook_instance):
    ansible_playbook_instance.add_cli_arg('foo', 'baz')

    assert 'baz' == ansible_playbook_instance._cli.get('foo')


def test_add_cli_arg_bool_false_not_added(ansible_playbook_instance):
    ansible_playbook_instance.add_cli_arg('bar', None)

    assert 'bar' not in ansible_playbook_instance._cli


def test_remove_cli_arg(ansible_playbook_instance):
    ansible_playbook_instance.remove_cli_arg('foo')

    assert 'foo' not in ansible_playbook_instance._cli


def test_add_env_arg(ansible_playbook_instance):
    ansible_playbook_instance.add_env_arg('FOO', 'bar')

    assert 'bar' == ansible_playbook_instance.env['FOO']


def test_add_env_arg_redefine_existing(ansible_playbook_instance):
    ansible_playbook_instance.add_env_arg('FOO', 'baz')

    assert 'baz' == ansible_playbook_instance.env['FOO']


def test_remove_env_arg(ansible_playbook_instance):
    ansible_playbook_instance.remove_env_arg('FOO')

    assert 'FOO' not in ansible_playbook_instance.env


def test_bake(ansible_playbook_instance):
    ansible_playbook_instance.bake()
    executable = sh.ansible_playbook
    expected = [
        '--diff', '--inventory-file=inventory_file', '--limit=all', '--sudo',
        '--timeout=30', '-vvvv', executable,
        ansible_playbook_instance._playbook
    ]

    assert expected == sorted(str(ansible_playbook_instance._ansible).split())


def test_bake_with_raw_ansible_args(mocker, ansible_playbook_instance):
    ansible_playbook_instance._raw_ansible_args = ('-v', '--foo', 'bar')
    ansible_playbook_instance.bake()

    assert re.search('-v --foo bar$', str(ansible_playbook_instance._ansible))


def test_ignores_host_group_vars():
    a = ansible_playbook.AnsiblePlaybook({
        'host_vars': 'foo',
        'group_vars': 'bar'
    }, {})

    assert not a._cli.get('host_vars')
    assert not a._cli.get('group_vars')


def test_execute(mocker, ansible_playbook_instance):
    mocker.patch('sh.ansible_playbook')
    result = ansible_playbook_instance.execute()

    assert isinstance(result, tuple)


def test_execute_exits_with_return_code_and_logs(patched_print_error,
                                                 ansible_playbook_instance):
    ansible_playbook_instance._ansible = sh.false.bake()
    false_path = sh.which('false')
    result = ansible_playbook_instance.execute()

    msg = "\n\n  RAN: '{0}'\n\n  STDOUT:\n\n\n  STDERR:\n".format(false_path)
    patched_print_error.assert_called_once_with(msg)

    assert (1, None) == result
