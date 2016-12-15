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
import sh

from molecule import config
from molecule.dependency import shell


@pytest.fixture()
def shell_instance(temp_files):
    confs = temp_files(fixtures=['molecule_vagrant_v1_config'])
    c = config.ConfigV1(configs=confs)
    c.config['dependency']['command'] = 'ls -l -a /tmp'

    return shell.Shell(c.config)


def test_execute(patched_run_command, shell_instance):
    shell_instance.execute()

    cmd = sh.ls.bake('-l', '-a', '/tmp')
    patched_run_command.assert_called_once_with(cmd, debug=False)


def test_execute_raises(patched_print_error, shell_instance):
    shell_instance._command = sh.false.bake()
    with pytest.raises(SystemExit) as e:
        shell_instance.execute()

    assert 1 == e.value.code

    false_path = sh.which('false')
    msg = "\n\n  RAN: '{0}'\n\n  STDOUT:\n\n\n  STDERR:\n".format(false_path)
    patched_print_error.assert_called_once_with(msg)
