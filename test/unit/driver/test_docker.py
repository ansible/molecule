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

from molecule import config
from molecule.driver import docker


@pytest.fixture
def docker_instance(config_instance):
    return docker.Docker(config_instance)


def test_config_private_member(docker_instance):
    assert isinstance(docker_instance._config, config.Config)


def test_testinfra_options_property(docker_instance):
    assert {'connection': 'docker'} == docker_instance.testinfra_options


def test_name_property(docker_instance):
    assert 'docker' == docker_instance.name


def test_options_property(docker_instance):
    assert {} == docker_instance.options


def test_inventory_property(docker_instance):
    x = {
        'instance-1-default': ['ansible_connection=docker'],
        'instance-2-default': ['ansible_connection=docker']
    }

    assert x == docker_instance.inventory
