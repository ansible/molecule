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

from molecule import status


@pytest.fixture
def status_instance():
    s = status.get_status()

    s.instance_name = None
    s.driver_name = None
    s.provisioner_name = None
    s.scenario_name = None
    s.created = None
    s.converged = None

    return s


def test_status_instance_name_attribute(status_instance):
    assert status_instance.instance_name is None


def test_status_driver_name_attribute(status_instance):
    assert status_instance.driver_name is None


def test_status_provisioner_name_attribute(status_instance):
    assert status_instance.provisioner_name is None


def test_status_scenario_name_attribute(status_instance):
    assert status_instance.scenario_name is None


def test_status_created_attribute(status_instance):
    assert status_instance.created is None


def test_status_converged_attribute(status_instance):
    assert status_instance.converged is None
