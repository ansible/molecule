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

from molecule import config


@pytest.fixture()
def default_config_data():
    return {'foo': 'bar', 'baz': 'qux'}


@pytest.fixture()
def project_config_data():
    return {'foo': 'bar', 'baz': 'project-override'}


@pytest.fixture()
def local_config_data():
    return {'foo': 'local-override', 'baz': 'local-override'}


@pytest.fixture()
def config_instance(temp_files):
    # TODO(retr0h): Rework molecule config so we can pass a generic
    # config here.  Molecule currently expects to find a 'vagrant'
    # key in this dict.
    c = temp_files(fixtures=['molecule_vagrant_config'])

    return config.Config(configs=c)


@pytest.fixture()
def mock_molecule_file_exists(monkeypatch):
    def mockreturn(m):
        return True

    return monkeypatch.setattr('molecule.config.Config.molecule_file_exists',
                               mockreturn)


def test_molecule_file(config_instance):
    assert 'molecule.yml' == config_instance.molecule_file


def test_build_config_paths(config_instance):
    # Full path provided to ``state_file``
    assert 'state_data.yml' == config_instance.config['molecule'][
        'state_file'].split('/')[-1]
    assert 'test/vagrantfile_file' == config_instance.config['molecule'][
        'vagrantfile_file']
    assert 'test/rakefile_file' == config_instance.config['molecule'][
        'rakefile_file']
    assert 'test/config_file' == config_instance.config['ansible'][
        'config_file']
    assert 'test/inventory_file' == config_instance.config['ansible'][
        'inventory_file']


def test_populate_instance_names(config_instance):
    config_instance.populate_instance_names('rhel-7')

    assert 'aio-01-rhel-7' == config_instance.config['vagrant']['instances'][
        0]['vm_name']


def test_molecule_file_exists(temp_files, mock_molecule_file_exists):
    configs = temp_files(fixtures=['molecule_vagrant_config'])
    c = config.Config(configs=configs)

    assert c.molecule_file_exists()


def test_molecule_file_does_not_exist(config_instance):
    assert not config_instance.molecule_file_exists()


def test_get_config(config_instance):
    assert isinstance(config_instance.config, dict)


def test_combine_default_config(temp_files):
    c = temp_files(fixtures=['default_config_data'])
    config_instance = config.Config(configs=c).config

    assert 'bar' == config_instance['foo']
    assert 'qux' == config_instance['baz']


def test_combine_project_config_overrides_default_config(temp_files):
    c = temp_files(fixtures=['default_config_data', 'project_config_data'])
    config_instance = config.Config(configs=c).config

    assert 'bar' == config_instance['foo']
    assert 'project-override' == config_instance['baz']


def test_combine_local_config_overrides_default_and_project_config(temp_files):
    c = temp_files(fixtures=['default_config_data', 'project_config_data',
                             'local_config_data'])
    config_instance = config.Config(configs=c).config

    assert 'local-override' == config_instance['foo']
    assert 'local-override' == config_instance['baz']
