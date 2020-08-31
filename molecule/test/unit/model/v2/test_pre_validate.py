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


@pytest.fixture
def _env():
    return {}


@pytest.fixture
def _keep_string():
    return "MOLECULE_"


def test_platforms_delegated(
    _model_platforms_delegated_section_data, _env, _keep_string
):
    assert (
        {}
        == schema_v3.pre_validate(
            _model_platforms_delegated_section_data, _env, _keep_string
        )[0]
    )


@pytest.fixture
def _model_platforms_delegated_errors_section_data():
    return """
---
platforms:
  - name: instance
""".strip()


@pytest.fixture
def _model_molecule_env_errors_section_data():
    return """
---
dependency:
  name: $MOLECULE_DEPENDENCY_NAME
driver:
  name: $MOLECULE_DRIVER_NAME
platforms:
  - name: instance
provisioner:
  name: $MOLECULE_PROVISIONER_NAME
verifier:
  name: $MOLECULE_VERIFIER_NAME
""".strip()


def test_has_errors_when_molecule_env_var_referenced_in_unallowed_sections(
    _model_molecule_env_errors_section_data, _env, _keep_string
):
    x = {
        "driver": [
            {
                "name": [
                    "cannot reference $MOLECULE special variables in this section",
                    "unallowed value $MOLECULE_DRIVER_NAME",
                ]
            }
        ],
        "dependency": [
            {
                "name": [
                    "cannot reference $MOLECULE special variables in this section",
                    "unallowed value $MOLECULE_DEPENDENCY_NAME",
                ]
            }
        ],
        "verifier": [
            {
                "name": [
                    "cannot reference $MOLECULE special variables in this section",
                    "unallowed value $MOLECULE_VERIFIER_NAME",
                ],
            }
        ],
        "provisioner": [
            {
                "name": [
                    "cannot reference $MOLECULE special variables in this section",
                    "unallowed value $MOLECULE_PROVISIONER_NAME",
                ],
            }
        ],
    }

    assert (
        x
        == schema_v3.pre_validate(
            _model_molecule_env_errors_section_data, _env, _keep_string
        )[0]
    )
