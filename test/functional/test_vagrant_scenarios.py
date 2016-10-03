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

import re

import os
import pytest
import sh

pytestmark = pytest.helpers.supports_vagrant()


def test_command_init(temp_dir):
    d = os.path.join(temp_dir, 'command-test')
    sh.molecule('init', '--role', 'command-test')
    os.chdir(d)
    sh.molecule('test')


@pytest.mark.parametrize(
    'scenario_setup', ['command_status'], indirect=['scenario_setup'])
def test_command_status(scenario_setup):
    out = sh.molecule('status', '--driver', 'vagrant', '--porcelain')

    assert re.search('status-scenario-01 .*not_created .*virtualbox',
                     out.stdout)
    assert re.search('status-scenario-02 .*not_created .*virtualbox',
                     out.stdout)


@pytest.mark.parametrize(
    'scenario_setup', ['command_test'], indirect=['scenario_setup'])
def test_command_test(scenario_setup):
    sh.molecule('test', '--driver', 'vagrant')


@pytest.mark.parametrize(
    'scenario_setup', ['command_test'], indirect=['scenario_setup'])
def test_command_test_platform_centos(scenario_setup):
    sh.molecule('test', '--driver', 'vagrant', '--platform', 'centos7')


@pytest.mark.parametrize(
    'scenario_setup', ['command_test'], indirect=['scenario_setup'])
def test_command_test_platform_all(scenario_setup):
    sh.molecule('test', '--driver', 'vagrant', '--platform', 'all')
