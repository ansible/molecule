#  Copyright (c) 2015-2016 Cisco Systems, Inc.
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

import subprocess

import pytest

from molecule.command import create


def test_execute_creates_instances(
        patched_driver_up, patched_create_templates, patched_remove_inventory,
        patched_create_inventory, patched_print_info, molecule_instance):
    c = create.Create({}, {}, molecule_instance)
    result = c.execute()

    patched_remove_inventory.assert_called_once
    patched_create_templates.assert_called_once

    msg = 'Creating instances ...'
    patched_print_info.assert_called_once_with(msg)
    assert molecule_instance.state.created
    patched_driver_up.assert_called_once_with(no_provision=True)
    (None, None) == result


def test_execute_creates_instances_with_platform_all(
        patched_driver_up, patched_create_templates, patched_remove_inventory,
        patched_create_inventory, molecule_instance):
    command_args = {'platform': 'all'}
    c = create.Create({}, command_args, molecule_instance)
    c.execute()

    patched_driver_up.assert_called_once_with(no_provision=True)
    assert molecule_instance.state.multiple_platforms


def test_execute_raises_on_exit(
        patched_driver_up, patched_create_templates, patched_remove_inventory,
        patched_create_inventory, patched_logger_error,
        patched_write_instances_state, molecule_instance):
    patched_driver_up.side_effect = subprocess.CalledProcessError(1, None,
                                                                  None)
    c = create.Create({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        c.execute()
    msg = "ERROR: Command 'None' returned non-zero exit status 1"
    patched_logger_error.assert_called_with(msg)
    assert not patched_create_inventory.called
    assert not patched_write_instances_state.called


def test_execute_does_not_raise_on_exit(
        patched_driver_up, patched_create_templates, patched_remove_inventory,
        patched_create_inventory, patched_logger_error,
        patched_write_instances_state, molecule_instance):
    patched_driver_up.side_effect = subprocess.CalledProcessError(1, None,
                                                                  None)
    c = create.Create({}, {}, molecule_instance)
    result = c.execute(exit=False)

    assert (1, '') == result
