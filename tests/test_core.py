#  Copyright (c) 2015-2016 Cisco Systems
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

import pytest

from molecule import core


class TestProvisioner():
    def __init__(self):
        self.instances = [{'name': 'demo-01',
                           'ansible_groups': ['demo', 'demo1'],
                           'options': {'append_platform_to_hostname': True}}]
        self._platform = 'centos7'


@pytest.fixture()
def molecule():
    m = core.Molecule(dict())
    m._provisioner = TestProvisioner()
    return m


def test_parse_provisioning_output_failure_00(molecule):
    failed_output = """
PLAY RECAP ********************************************************************
vagrant-01-ubuntu              : ok=36   changed=29   unreachable=0    failed=0
    """
    res, changed_tasks = molecule._parse_provisioning_output(failed_output)

    assert not res


def test_parse_provisioning_output_failure_01(molecule):
    failed_output = """
PLAY RECAP ********************************************************************
NI: common | Non idempotent task for testing
common-01-rhel-7           : ok=18   changed=14   unreachable=0    failed=0
    """
    res, changed_tasks = molecule._parse_provisioning_output(failed_output)

    assert not res
    assert 1 == len(changed_tasks)


def test_parse_provisioning_output_success_00(molecule):
    success_output = """
PLAY RECAP ********************************************************************
vagrant-01-ubuntu              : ok=36   changed=0    unreachable=0    failed=0
    """
    res, changed_tasks = molecule._parse_provisioning_output(success_output)

    assert res
    assert [] == changed_tasks


def test_instances_state_00(molecule):
    success_output = {'demo-01-centos7': {'groups': ['demo', 'demo1']}}
    assert success_output == molecule._instances_state()
