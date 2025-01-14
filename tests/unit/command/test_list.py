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

from typing import TYPE_CHECKING

from molecule.command import list  # noqa: A004
from molecule.status import Status


if TYPE_CHECKING:
    import pytest

    from molecule import config


def test_list_execute(  # noqa: D103
    capsys: pytest.CaptureFixture[str],
    config_instance: config.Config,
) -> None:
    l = list.List(config_instance)  # noqa: E741
    x = [
        Status(
            instance_name="instance-1",
            driver_name="default",
            provisioner_name="ansible",
            scenario_name="default",
            created="false",
            converged="false",
        ),
        Status(
            instance_name="instance-2",
            driver_name="default",
            provisioner_name="ansible",
            scenario_name="default",
            created="false",
            converged="false",
        ),
    ]

    assert x == l.execute()
