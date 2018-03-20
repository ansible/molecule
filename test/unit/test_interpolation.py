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
        'FOO': 'foo',
        'BAR': '',
        'DEPENDENCY_NAME': 'galaxy',
        'VERIFIER_NAME': 'testinfra'
    }


@pytest.fixture
def _instance(_mock_env):
    return interpolation.Interpolator(interpolation.TemplateWithDefaults,
                                      _mock_env).interpolate


def test_escaped_interpolation(_instance):
    assert '${foo}' == _instance('$${foo}')


def test_invalid_interpolation(_instance):
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('${')
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('$}')
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('${}')
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('${ }')
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('${ foo}')
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('${foo }')
    with pytest.raises(interpolation.InvalidInterpolation):
        _instance('${foo!}')


def test_interpolate_missing_no_default(_instance):
    assert 'This  var' == _instance('This ${missing} var')
    assert 'This  var' == _instance('This ${BAR} var')


def test_interpolate_with_value(_instance):
    assert 'This foo var' == _instance('This $FOO var')
    assert 'This foo var' == _instance('This ${FOO} var')


def test_interpolate_missing_with_default(_instance):
    assert 'ok def' == _instance('ok ${missing:-def}')
    assert 'ok def' == _instance('ok ${missing-def}')
    assert 'ok /non:-alphanumeric' == _instance(
        'ok ${BAR:-/non:-alphanumeric}')


def test_interpolate_with_empty_and_default_value(_instance):
    assert 'ok def' == _instance('ok ${BAR:-def}')
    assert 'ok ' == _instance('ok ${BAR-def}')


def test_interpolate_with_molecule_yaml(_instance):
    data = """
---
dependency:
    name: $DEPENDENCY_NAME
driver:
    name: docker
lint:
    name: yamllint
platforms:
  - name: instance-1
provisioner:
    name: ansible
scenario:
    name: default
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
    name: docker
lint:
    name: yamllint
platforms:
  - name: instance-1
provisioner:
    name: ansible
scenario:
    name: default
verifier:
    name: testinfra
    options:
      foo: bar
""".strip()

    assert x == _instance(data)
