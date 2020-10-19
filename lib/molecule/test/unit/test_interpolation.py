# Copyright 2015 Docker, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pytest

from molecule import interpolation


@pytest.fixture
def _mock_env():
    return {
        "FOO": "foo",
        "BAR": "",
        "DEPENDENCY_NAME": "galaxy",
        "VERIFIER_NAME": "ansible",
        "MOLECULE_SCENARIO_NAME": "default",
    }


@pytest.fixture
def _instance(_mock_env):
    return interpolation.Interpolator(interpolation.TemplateWithDefaults, _mock_env)


def test_escaped_interpolation(_instance):
    assert "${foo}" == _instance.interpolate("$${foo}")


def test_invalid_interpolation(_instance):
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("${")
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("$}")
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("${}")
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("${ }")
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("${ foo}")
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("${foo }")
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance.interpolate("${foo!}")


def test_interpolate_missing_no_default(_instance):
    assert "This  var" == _instance.interpolate("This ${missing} var")
    assert "This  var" == _instance.interpolate("This ${BAR} var")


def test_interpolate_with_value(_instance):
    assert "This foo var" == _instance.interpolate("This $FOO var")
    assert "This foo var" == _instance.interpolate("This ${FOO} var")


def test_interpolate_missing_with_default(_instance):
    assert "ok def" == _instance.interpolate("ok ${missing:-def}")
    assert "ok def" == _instance.interpolate("ok ${missing-def}")
    assert "ok /non:-alphanumeric" == _instance.interpolate(
        "ok ${BAR:-/non:-alphanumeric}"
    )


def test_interpolate_with_empty_and_default_value(_instance):
    assert "ok def" == _instance.interpolate("ok ${BAR:-def}")
    assert "ok " == _instance.interpolate("ok ${BAR-def}")


def test_interpolate_interpolates_MOLECULE_strings(_instance):
    assert "default" == _instance.interpolate("$MOLECULE_SCENARIO_NAME")


def test_interpolate_does_not_interpolate_MOLECULE_strings(_instance):
    assert "foo $MOLECULE_SCENARIO_NAME" == _instance.interpolate(
        "foo $MOLECULE_SCENARIO_NAME", keep_string="MOLECULE_"
    )


def test_interpolate_with_molecule_yaml(_instance):
    data = """
---
dependency:
    name: $DEPENDENCY_NAME
driver:
    name: delegated
platforms:
  - name: instance-1
provisioner:
    name: ansible
verifier:
    name: ${VERIFIER_NAME}
    options:
      $FOO: bar
""".strip()

    x = """
---
dependency:
    name: galaxy
driver:
    name: delegated
platforms:
  - name: instance-1
provisioner:
    name: ansible
verifier:
    name: ansible
    options:
      foo: bar
""".strip()

    assert x == _instance.interpolate(data)
