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

import subprocess

import pytest

from molecule.command import destroy


def test_execute_deletes_instances(
        patched_driver_destroy, patched_print_info, patched_remove_templates,
        patched_remove_inventory, molecule_instance):
    d = destroy.Destroy({}, {}, molecule_instance)
    result = d.execute()

    msg = 'Destroying instances...'
    patched_print_info.assert_called_once_with(msg)

    patched_driver_destroy.assert_called_once_with()
    assert not molecule_instance.state.created
    assert not molecule_instance.state.converged
    (None, None) == result

    patched_remove_templates.assert_called_once_with()
    patched_remove_inventory.assert_called_once_with()


def test_execute_raises_on_exit(patched_driver_destroy, patched_print_info,
                                patched_print_error, patched_remove_templates,
                                patched_remove_inventory, molecule_instance):
    patched_driver_destroy.side_effect = subprocess.CalledProcessError(1, None,
                                                                       None)

    d = destroy.Destroy({}, {}, molecule_instance)
    with pytest.raises(SystemExit):
        d.execute()

    msg = "Command 'None' returned non-zero exit status 1"
    patched_print_error.assert_called_with(msg)

    assert not patched_remove_templates.called
    assert not patched_remove_inventory.called


def test_execute_does_not_raise_on_exit(patched_driver_destroy,
                                        patched_print_info, molecule_instance):
    patched_driver_destroy.side_effect = subprocess.CalledProcessError(1, None,
                                                                       None)
    d = destroy.Destroy({}, {}, molecule_instance)
    result = d.execute(exit=False)

    assert (1, '') == result
