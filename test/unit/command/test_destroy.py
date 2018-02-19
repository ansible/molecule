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

from molecule.command import destroy


def test_execute(mocker, patched_destroy_prune, patched_logger_info,
                 patched_ansible_destroy, config_instance):
    d = destroy.Destroy(config_instance)
    d.execute()

    x = [
        mocker.call("Scenario: 'default'"),
        mocker.call("Action: 'destroy'"),
    ]
    assert x == patched_logger_info.mock_calls

    patched_ansible_destroy.assert_called_once_with()

    assert not config_instance.state.converged
    assert not config_instance.state.created
    patched_destroy_prune.assert_called_once_with()


def test_execute_skips_when_destroy_strategy_is_never(
        patched_destroy_setup, molecule_driver_delegated_section_data,
        patched_logger_warn, patched_ansible_destroy, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_delegated_section_data)
    config_instance.command_args = {'destroy': 'never'}

    d = destroy.Destroy(config_instance)
    d.execute()

    msg = "Skipping, '--destroy=never' requested."
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_destroy.called


def test_execute_skips_when_delegated_driver(
        patched_destroy_setup, molecule_driver_delegated_section_data,
        patched_logger_warn, patched_ansible_destroy, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_driver_delegated_section_data)
    d = destroy.Destroy(config_instance)
    d.execute()

    msg = 'Skipping, instances are delegated.'
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_destroy.called
