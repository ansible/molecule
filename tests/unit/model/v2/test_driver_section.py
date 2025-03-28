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

from molecule.model import schema_v3


@pytest.fixture
def _model_driver_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "driver": {
            "name": "default",
            "provider": {"name": None},
            "options": {"managed": True},
            "ssh_connection_options": ["foo", "bar"],
            "safe_files": ["foo", "bar"],
        },
    }


@pytest.mark.parametrize("config", ["_model_driver_section_data"], indirect=True)  # noqa: PT007
def test_driver(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)


@pytest.fixture
def _model_driver_errors_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "driver": {
            "name": 0,
        },
    }


@pytest.fixture
def _model_driver_errors_section_data_no_prefix():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {
        "driver": {
            "name": "random_name",
        },
    }


@pytest.mark.parametrize(
    "config",
    [  # noqa: PT007
        "_model_driver_errors_section_data",
        "_model_driver_errors_section_data_no_prefix",
    ],
    indirect=True,
)
def test_driver_has_errors(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    base_error_msg = "is not one of ['azure', 'ec2', 'delegated', 'docker', 'containers', 'openstack', 'podman', 'vagrant', 'digitalocean', 'gce', 'libvirt', 'lxd', 'molecule-*', 'molecule_*', 'custom-*', 'custom_*']"

    driver_name = str(config["driver"]["name"])
    if isinstance(config["driver"]["name"], str):
        # add single quotes for string
        driver_name = f"'{config['driver']['name']}'"

    error_msg = [f"{driver_name} {base_error_msg}"]
    assert error_msg == schema_v3.validate(config)


@pytest.fixture
def _model_driver_provider_name_nullable_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"provider": {"name": None}}}


@pytest.mark.parametrize(
    "config",
    ["_model_driver_provider_name_nullable_section_data"],  # noqa: PT007
    indirect=True,
)
def test_driver_provider_name_nullable(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)


@pytest.fixture
def _model_driver_allows_delegated_section_data():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"name": "default"}}


@pytest.fixture
def _model_driver_allows_molecule_section_data1():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"name": "molecule-test_driver.name"}}


@pytest.fixture
def _model_driver_allows_molecule_section_data2():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"name": "molecule_test_driver.name"}}


@pytest.fixture
def _model_driver_allows_custom_section_data1():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"name": "custom-test_driver.name"}}


@pytest.fixture
def _model_driver_allows_custom_section_data2():  # type: ignore[no-untyped-def]  # noqa: ANN202
    return {"driver": {"name": "custom_test_driver.name"}}


###
@pytest.mark.parametrize(
    "config",
    [  # noqa: PT007
        ("_model_driver_allows_delegated_section_data"),
        ("_model_driver_allows_molecule_section_data1"),
        ("_model_driver_allows_molecule_section_data2"),
        ("_model_driver_allows_custom_section_data2"),
        ("_model_driver_allows_custom_section_data1"),
    ],
    indirect=True,
)
def test_driver_allows_name(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)
