#  Copyright (c) 2015-2018 Cisco Systems, Inc.
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

from molecule.model import schema_v3


@pytest.fixture()
def _model_driver_section_data():
    return {
        "driver": {
            "name": "delegated",
            "provider": {"name": None},
            "options": {"managed": True},
            "ssh_connection_options": ["foo", "bar"],
            "safe_files": ["foo", "bar"],
        },
    }


@pytest.mark.parametrize("_config", ["_model_driver_section_data"], indirect=True)
def test_driver(_config):
    assert not schema_v3.validate(_config)


@pytest.fixture()
def _model_driver_errors_section_data():
    return {
        "driver": {
            "name": 0,
        },
    }


@pytest.fixture()
def _model_driver_errors_section_data_no_prefix():
    return {
        "driver": {
            "name": "random_name",
        },
    }


@pytest.mark.parametrize(
    "_config",
    [
        "_model_driver_errors_section_data",
        "_model_driver_errors_section_data_no_prefix",
    ],
    indirect=True,
)
def test_driver_has_errors(_config):
    base_error_msg = "is not one of ['azure', 'ec2', 'delegated', 'docker', 'containers', 'openstack', 'podman', 'vagrant', 'digitalocean', 'gce', 'libvirt', 'lxd', 'molecule-*', 'molecule_*', 'custom-*', 'custom_*']"

    driver_name = str(_config["driver"]["name"])
    if isinstance(_config["driver"]["name"], str):
        # add single quotes for string
        driver_name = f"'{_config['driver']['name']}'"

    error_msg = [f"{driver_name} {base_error_msg}"]
    assert error_msg == schema_v3.validate(_config)


@pytest.fixture()
def _model_driver_provider_name_nullable_section_data():
    return {"driver": {"provider": {"name": None}}}


@pytest.mark.parametrize(
    "_config",
    ["_model_driver_provider_name_nullable_section_data"],
    indirect=True,
)
def test_driver_provider_name_nullable(_config):
    assert not schema_v3.validate(_config)


@pytest.fixture()
def _model_driver_allows_delegated_section_data():
    return {"driver": {"name": "delegated"}}


@pytest.fixture()
def _model_driver_allows_molecule_section_data1():
    return {"driver": {"name": "molecule-test_driver.name"}}


@pytest.fixture()
def _model_driver_allows_molecule_section_data2():
    return {"driver": {"name": "molecule_test_driver.name"}}


@pytest.fixture()
def _model_driver_allows_custom_section_data1():
    return {"driver": {"name": "custom-test_driver.name"}}


@pytest.fixture()
def _model_driver_allows_custom_section_data2():
    return {"driver": {"name": "custom_test_driver.name"}}


###
@pytest.mark.parametrize(
    "_config",
    [
        ("_model_driver_allows_delegated_section_data"),
        ("_model_driver_allows_molecule_section_data1"),
        ("_model_driver_allows_molecule_section_data2"),
        ("_model_driver_allows_custom_section_data2"),
        ("_model_driver_allows_custom_section_data1"),
    ],
    indirect=True,
)
def test_driver_allows_name(_config):
    assert not schema_v3.validate(_config)
