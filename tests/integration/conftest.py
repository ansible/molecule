#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
#  Copyright (c) 2018 Red Hat, Inc.
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

from typing import TYPE_CHECKING

import pytest

from molecule import logger
from molecule.app import get_app


if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


LOG = logger.get_logger(__name__)


@pytest.fixture(name="with_scenario")
def _with_scenario(  # noqa: PLR0913
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    test_ephemeral_dir_env: dict[str, str],
    scenario_to_test: str,
    scenario_name: str,
    test_fixture_dir: Path,
) -> Iterator[None]:
    """Yield to test with a scenario, changes dir and does cleanup.

    Args:
        request: The pytest request object.
        monkeypatch: The pytest monkeypatch object.
        test_ephemeral_dir_env: The ephemeral directory environment variables.
        scenario_to_test: The scenario to test.
        scenario_name: The scenario name.
        test_fixture_dir: The test fixture directory.

    Yields:
        None:
    """
    scenario_directory = test_fixture_dir / "scenarios" / scenario_to_test

    monkeypatch.chdir(scenario_directory)

    yield
    if request.node.rep_call.failed:
        return
    if scenario_name:
        msg = f"CLEANUP: Destroying instances for {scenario_name}"
        LOG.info(msg)
        cmd = ["molecule", "destroy", "--scenario-name", scenario_name]
        assert (
            get_app(scenario_directory).run_command(cmd=cmd, env=test_ephemeral_dir_env).returncode
            == 0
        )
