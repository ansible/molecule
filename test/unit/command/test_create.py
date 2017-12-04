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

from molecule.command import create


def test_execute(mocker, patched_logger_info, patched_ansible_create,
                 config_instance):
    c = create.Create(config_instance)
    c.execute()

    x = [
        mocker.call("Scenario: 'default'"),
        mocker.call("Action: 'create'"),
    ]
    assert x == patched_logger_info.mock_calls

    assert 'docker' == config_instance.state.driver

    patched_ansible_create.assert_called_once_with()

    assert config_instance.state.created


def test_execute_skips_when_delegated_driver(
        patched_create_setup, molecule_driver_delegated_section_data,
        patched_logger_warn, patched_ansible_create, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_delegated_section_data)
    c = create.Create(config_instance)
    c.execute()

    msg = 'Skipping, instances are delegated.'
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_create.called


def test_execute_skips_when_instances_already_created(
        patched_logger_warn, patched_ansible_create, config_instance):
    config_instance.state.change_state('created', True)
    c = create.Create(config_instance)
    c.execute()

    msg = 'Skipping, instances already created.'
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_create.called
