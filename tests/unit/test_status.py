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

import pytest

from molecule.status import Status


@pytest.fixture
def _instance() -> Status:
    s = Status(
        instance_name="instance",
        driver_name="driver",
        provisioner_name="provisioner",
        scenario_name="scenario",
        created="True",
        converged="False",
    )

    return s  # noqa: RET504


def test__instance_name_attribute(_instance: Status) -> None:  # noqa: PT019, D103
    assert _instance.instance_name == "instance"


def test_status_driver_name_attribute(_instance: Status) -> None:  # noqa: PT019, D103
    assert _instance.driver_name == "driver"


def test_status_provisioner_name_attribute(_instance: Status) -> None:  # noqa: PT019, D103
    assert _instance.provisioner_name == "provisioner"


def test_status_scenario_name_attribute(_instance: Status) -> None:  # noqa: PT019, D103
    assert _instance.scenario_name == "scenario"


def test_status_created_attribute(_instance: Status) -> None:  # noqa: PT019, D103
    assert _instance.created == "True"


def test_status_converged_attribute(_instance: Status) -> None:  # noqa: PT019, D103
    assert _instance.converged == "False"
