#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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
from __future__ import annotations

import unittest

from io import StringIO
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from molecule.command import converge
from molecule.shell import main


if TYPE_CHECKING:
    from unittest.mock import Mock

    import pytest

    from pytest_mock import MockerFixture

    from molecule import config


# NOTE(retr0h): The use of the `patched_config_validate` fixture, disables
# config.Config._validate from executing.  Thus preventing odd side-effects
# throughout patched.assert_called unit tests.
def test_converge_execute(  # noqa: D103
    mocker: MockerFixture,  # noqa: ARG001
    caplog: pytest.LogCaptureFixture,
    patched_ansible_converge: Mock,
    patched_config_validate: Any,  # noqa: ANN401, ARG001
    config_instance: config.Config,
) -> None:
    c = converge.Converge(config_instance)
    c.execute()

    assert "default" in caplog.text
    assert "converge" in caplog.text

    patched_ansible_converge.assert_called_once_with()

    assert config_instance.state.converged


class TestConverge(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stderr", new_callable=StringIO)
    @patch("molecule.scenarios.Scenarios")
    @patch("molecule.command.base.get_configs")
    def test_ansible_args_passed_to_scenarios_get_configs(
        self,
        patched_get_configs,
        mock_scenarios,
        mock_stdout,
        mock_stderr,
    ):
        args = ["converge", "--", "-e", "testvar=testvalue"]
        with patch("sys.argv", ["main"] + args):
            try:
                main()
            except SystemExit as e:
                self.assertEqual(e.code, 0)

        ansible_args = args[2:]
        # call index [0][2] is the 3rd positional argument to get_configs,
        # which should be the tuple of parsed ansible_args from the CLI
        self.assertEqual(patched_get_configs.call_args[0][2], tuple(ansible_args))


if __name__ == "__main__":
    unittest.main()
