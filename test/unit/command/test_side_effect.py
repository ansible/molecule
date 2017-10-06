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

import pytest

from molecule.command import side_effect


@pytest.fixture
def molecule_provisioner_section_with_side_effect_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'side_effect': 'side_effect.yml',
            },
        }
    }


def test_execute(mocker, molecule_provisioner_section_with_side_effect_data,
                 patched_ansible_side_effect, patched_logger_info,
                 config_instance):
    config_instance.merge_dicts(
        config_instance.config,
        molecule_provisioner_section_with_side_effect_data)

    se = side_effect.SideEffect(config_instance)
    se.execute()

    x = [
        mocker.call("Scenario: 'default'"),
        mocker.call("Action: 'side_effect'"),
    ]
    assert x == patched_logger_info.mock_calls

    patched_ansible_side_effect.assert_called_once_with()


def test_execute_skips_when_playbook_not_configured(
        patched_logger_warn, patched_ansible_side_effect, config_instance):
    se = side_effect.SideEffect(config_instance)
    se.execute()

    msg = 'Skipping, side effect playbook not configured.'
    patched_logger_warn.assert_called_once_with(msg)

    assert not patched_ansible_side_effect.called
