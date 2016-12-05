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

from molecule.command import destroy


def test_execute(mocker, patched_print_info, patched_ansible_playbook,
                 patched_ansible_playbook_execute, config_instance):
    d = destroy.Destroy(config_instance)
    d.execute()
    x = [
        mocker.call('Scenario: [default]'),
        mocker.call('Provisioner: [ansible]'),
        mocker.call('Playbook: [destroy.yml]')
    ]

    assert x == patched_print_info.mock_calls

    pb = os.path.join(config_instance.scenario_directory, 'destroy.yml')
    patched_ansible_playbook.assert_called_once_with(
        pb, config_instance.inventory_file, config_instance)

    patched_ansible_playbook_execute.assert_called_once
