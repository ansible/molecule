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

from molecule import config
from molecule.driver import dockr


@pytest.fixture
def driver_data():
    return {'driver': {'name': 'docker', 'options': {}}}


@pytest.fixture
def docker_instance(molecule_file, platforms_data, driver_data):
    configs = [platforms_data, driver_data]
    c = config.Config(molecule_file, configs=configs)

    return dockr.Dockr(c)


def test_config_private_member(docker_instance):
    assert isinstance(docker_instance._config, config.Config)


def test_testinfra_options_property(docker_instance):
    assert {'connection': 'docker'} == docker_instance.testinfra_options


def test_connection_options_property(docker_instance):
    x = {'ansible_connection': 'docker'}

    assert x == docker_instance.connection_options


def test_name_property(docker_instance):
    assert 'docker' == docker_instance.name


def test_options_property(docker_instance):
    assert {} == docker_instance.options


def test_status(mocker, docker_instance):
    def side_effect(filters):
        instance_name = filters['name']

        return [{
            u'Status': u'Up About an hour',
            u'State': u'running',
            u'Command': u'sleep infinity',
            u'Names': [u'/{}'.format(instance_name)],
        }]

    m = mocker.patch('docker.client.Client.containers')
    m.side_effect = side_effect
    result = docker_instance.status()

    assert 2 == len(result)

    assert result[0].name == 'instance-1-default'
    assert result[0].state == 'Up About an hour'
    assert result[0].driver == 'Docker'

    assert result[1].name == 'instance-2-default'
    assert result[1].state == 'Up About an hour'
    assert result[1].driver == 'Docker'


def test_status_not_created(mocker, docker_instance):
    m = mocker.patch('docker.client.Client.containers')
    m.return_value = []
    result = docker_instance.status()

    assert 2 == len(result)

    assert result[0].name == 'instance-1-default'
    assert result[0].state == 'Not Created'
    assert result[0].driver == 'Docker'

    assert result[1].name == 'instance-2-default'
    assert result[1].state == 'Not Created'
    assert result[1].driver == 'Docker'
