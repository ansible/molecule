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

import os
import re

import pytest

from molecule import config
from molecule.provisioner import ansible


@pytest.fixture
def ansible_instance(config_instance):
    return ansible.Ansible(config_instance)


def test_config_private_member(ansible_instance):
    assert isinstance(ansible_instance._config, config.Config)


def test_converge(ansible_instance, patched_ansible_playbook,
                  patched_ansible_playbook_execute):
    ansible_instance.converge('inventory', 'playbook')

    patched_ansible_playbook.assert_called_once_with('inventory', 'playbook',
                                                     ansible_instance._config)
    patched_ansible_playbook_execute.assert_called_once


def test_write_inventory(temp_dir, ansible_instance):
    ansible_instance.write_inventory()

    assert os.path.exists(ansible_instance._config.inventory_file)

    content = open(ansible_instance._config.inventory_file, 'r').read()
    assert re.search(r'# Molecule managed', content)
    assert re.search(r'instance-1-default ansible_connection=docker', content)
    assert re.search(r'instance-2-default ansible_connection=docker', content)

    assert re.search(r'\[bar\].*?instance-1-default.*?(\[\w+])?', content,
                     re.DOTALL)
    assert re.search(
        r'\[foo\].*?instance-1-default.*?instance-2-default.*?(\[\w+])?',
        content, re.DOTALL)
    assert re.search(r'\[baz\].*?instance-2-default.*?(\[\w+])?', content,
                     re.DOTALL)


def test_write_inventory_handles_missing_groups(temp_dir, ansible_instance):
    platforms = [{'name': 'instance-1'}, {'name': 'instance-2'}]
    ansible_instance._config.config['platforms'] = platforms
    ansible_instance.write_inventory()

    assert os.path.exists(ansible_instance._config.inventory_file)


def test_write_inventory_prints_error_when_missing_hosts(
        temp_dir, patched_print_error, ansible_instance):
    ansible_instance._config.config['platforms'] = []
    with pytest.raises(SystemExit) as e:
        ansible_instance.write_inventory()

    assert 1 == e.value.code

    msg = "Instances missing from the 'platform' section of molecule.yml."
    patched_print_error.assert_called_once_with(msg)
