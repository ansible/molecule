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

from molecule.model import schema_v2


@pytest.fixture
def _model_platforms_docker_section_data():
    return """
---
platforms:
  - name: instance
    registry:
      credentials:
        password: $BAR
""".strip()


@pytest.fixture
def _env():
    return {}


@pytest.fixture
def _keep_string():
    return 'MOLECULE_'


@pytest.mark.parametrize('_stream', [(_model_platforms_docker_section_data)])
def test_platforms_docker(_stream, _env, _keep_string):
    assert {} == schema_v2.pre_validate(_stream(), _env, _keep_string)


@pytest.fixture
def _model_platforms_docker_errors_section_data():
    return """
---
platforms:
  - name: instance
    registry:
      credentials:
        password: 123
""".strip()


@pytest.mark.parametrize('_stream',
                         [_model_platforms_docker_errors_section_data])
def test_platforms_docker_has_errors(_stream, _env, _keep_string):
    x = {
        'platforms': [{
            0: [{
                'registry': [{
                    'credentials': [{
                        'password': ['must be of string type']
                    }]
                }]
            }]
        }]
    }

    assert x == schema_v2.pre_validate(_stream(), _env, _keep_string)


@pytest.fixture
def _model_molecule_env_errors_section_data():
    return """
---
dependency:
  name: $MOLECULE_DEPENDENCY_NAME
driver:
  name: $MOLECULE_DRIVER_NAME
lint:
  name: $MOLECULE_LINT_NAME
platforms:
  - name: instance
    image: centos:latest
    networks:
      - name: foo
      - name: bar
provisioner:
  name: $MOLECULE_PROVISIONER_NAME
  lint:
    name: $MOLECULE_PROVISIONER_LINT_NAME
scenario:
  name: $MOLECULE_SCENARIO_NAME
verifier:
  name: $MOLECULE_VERIFIER_NAME
  lint:
    name: $MOLECULE_VERIFIER_LINT_NAME
""".strip()


@pytest.mark.parametrize('_stream',
                         [(_model_molecule_env_errors_section_data)])
def test_has_errors_when_molecule_env_var_referenced_in_unallowed_sections(
        _stream, _env, _keep_string):
    x = {
        'scenario': [{
            'name':
            ['cannot reference $MOLECULE special variables in this section']
        }],
        'lint': [{
            'name': [
                'cannot reference $MOLECULE special variables in this section',
                'unallowed value $MOLECULE_LINT_NAME'
            ]
        }],
        'driver': [{
            'name': [
                'cannot reference $MOLECULE special variables in this section',
                'unallowed value $MOLECULE_DRIVER_NAME'
            ]
        }],
        'dependency': [{
            'name': [
                'cannot reference $MOLECULE special variables in this section',
                'unallowed value $MOLECULE_DEPENDENCY_NAME'
            ]
        }],
        'verifier': [{
            'lint': [{
                'name':
                [('cannot reference $MOLECULE special variables in this '
                  'section'), 'unallowed value $MOLECULE_VERIFIER_LINT_NAME']
            }],
            'name': [
                'cannot reference $MOLECULE special variables in this section',
                'unallowed value $MOLECULE_VERIFIER_NAME'
            ]
        }],
        'provisioner': [{
            'lint': [{
                'name':
                [('cannot reference $MOLECULE special variables in this '
                  'section'),
                 'unallowed value $MOLECULE_PROVISIONER_LINT_NAME']
            }],
            'name': [
                'cannot reference $MOLECULE special variables in this section',
                'unallowed value $MOLECULE_PROVISIONER_NAME'
            ]
        }]
    }

    assert x == schema_v2.pre_validate(_stream(), _env, _keep_string)
