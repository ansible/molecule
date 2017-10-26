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

from molecule.command import prepare


def test_execute(mocker, patched_logger_info, patched_ansible_prepare,
                 config_instance):
    m = mocker.patch('molecule.command.prepare.Prepare._has_prepare_playbook')
    m.return_value = True

    p = prepare.Prepare(config_instance)
    p.execute()

    x = [
        mocker.call("Scenario: 'default'"),
        mocker.call("Action: 'prepare'"),
    ]
    assert x == patched_logger_info.mock_calls

    patched_ansible_prepare.assert_called_once_with()

    assert config_instance.state.prepared


def test_execute_skips_when_instances_already_prepared(
        patched_logger_warn, patched_ansible_prepare, config_instance):
    config_instance.state.change_state('prepared', True)
    p = prepare.Prepare(config_instance)
    p.execute()

    msg = 'Skipping, instances already prepared.'
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_prepare.called


def test_execute_when_instances_already_prepared_but_force_provided(
        mocker, patched_logger_warn, patched_ansible_prepare, config_instance):
    m = mocker.patch('molecule.command.prepare.Prepare._has_prepare_playbook')
    m.return_value = True
    config_instance.state.change_state('prepared', True)
    config_instance.command_args = {'force': True}

    p = prepare.Prepare(config_instance)
    p.execute()

    patched_ansible_prepare.assert_called_once_with()


def test_execute_logs_deprecation_when_prepare_yml_missing(
        mocker, patched_logger_warn, patched_ansible_create,
        patched_ansible_prepare, config_instance):
    m = mocker.patch('molecule.command.prepare.Prepare._has_prepare_playbook')
    m.return_value = False

    p = prepare.Prepare(config_instance)
    p.execute()

    msg = ('[DEPRECATION WARNING]:\n  The prepare playbook not found '
           'at {}/prepare.yml.  Please add one to the scenarios '
           'directory.').format(config_instance.scenario.directory)
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_prepare.called

    assert config_instance.state.prepared


def test_has_prepare_playbook(config_instance):
    p = prepare.Prepare(config_instance)

    assert not p._has_prepare_playbook()
