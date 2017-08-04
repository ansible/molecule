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

import collections
import os

import pytest

from molecule import migrate


@pytest.fixture
def migrate_instance():
    molecule_file = os.path.join(
        os.path.dirname(__file__), os.path.pardir, 'resources',
        'molecule_v1_vagrant.yml')

    return migrate.Migrate(molecule_file)


def test_get_v1_config(migrate_instance):
    data = migrate_instance._get_v1_config()

    assert isinstance(data, dict)


def test_v1_member(migrate_instance):
    assert isinstance(migrate_instance._v1, dict)


def test_v2_member(migrate_instance):
    assert isinstance(migrate_instance._v2, collections.OrderedDict)


def test_dump(migrate_instance):
    x = """
---
dependency:
  name: galaxy
driver:
  name: vagrant
  provider:
    name: virtualbox
lint:
  name: yamllint
platforms:
  - name: host.example.com
    box: namespace/rhel-7
    box_version: 7.2.0
    box_url: http://example.com/pub/rhel-7.json
    memory: 4096
    cpus: 2
    groups:
      - group1
      - group2
    interfaces:
      - auto_config: true
        network_name: private_network
        type: dhcp
    raw_config_args:
      - foo
      - bar
provisioner:
  name: ansible
  env:
    foo: bar
  options:
    extra-vars: foo=bar
    verbose: true
    become: true
    tags: foo,bar
  lint:
    name: ansible-lint
scenario:
  name: default
verifier:
  name: testinfra
  options:
    sudo: true
  lint:
    name: flake8
""".lstrip()

    assert x == migrate_instance.dump()


def test_convert(migrate_instance, patched_logger_info):
    x = {
        'scenario': {
            'name': 'default',
        },
        'platforms': [{
            'box':
            'namespace/rhel-7',
            'box_version':
            '7.2.0',
            'name':
            'host.example.com',
            'interfaces': [{
                'type': 'dhcp',
                'network_name': 'private_network',
                'auto_config': True,
            }],
            'cpus':
            2,
            'box_url':
            'http://example.com/pub/rhel-7.json',
            'groups': [
                'group1',
                'group2',
            ],
            'memory':
            4096,
            'raw_config_args': [
                'foo',
                'bar',
            ],
        }],
        'lint': {
            'name': 'yamllint',
        },
        'driver': {
            'name': 'vagrant',
            'provider': {
                'name': 'virtualbox',
            },
        },
        'dependency': {
            'name': 'galaxy',
        },
        'verifier': {
            'lint': {
                'name': 'flake8',
            },
            'name': 'testinfra',
            'options': {
                'sudo': True,
            }
        },
        'provisioner': {
            'lint': {
                'name': 'ansible-lint',
            },
            'name': 'ansible',
            'env': {
                'foo': 'bar',
            },
            'options': {
                'become': True,
                'extra-vars': 'foo=bar',
                'verbose': True,
                'tags': 'foo,bar',
            }
        }
    }

    data = migrate_instance._convert()
    assert x == migrate_instance._to_dict(data)

    msg = 'Vagrant syle v1 config found'
    patched_logger_info.assert_called_once_with(msg)


def test_convert_raises_on_invalid_migration_config(migrate_instance,
                                                    patched_logger_critical):
    del migrate_instance._v1['vagrant']

    with pytest.raises(SystemExit) as e:
        migrate_instance._convert()

    assert 1 == e.value.code

    msg = 'Vagrant migrations only supported.  Exiting.'
    patched_logger_critical.assert_called_once_with(msg)
