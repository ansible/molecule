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
def _model_verifier_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'enabled': True,
            'directory': 'foo',
            'options': {
                'foo': 'bar'
            },
            'env': {
                'FOO': 'foo',
                'FOO_BAR': 'foo_bar',
            },
            'additional_files_or_dirs': [
                'foo',
            ],
            'lint': {
                'name': 'flake8',
                'enabled': True,
                'options': {
                    'foo': 'bar',
                },
                'env': {
                    'FOO': 'foo',
                    'FOO_BAR': 'foo_bar',
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_section_data'], indirect=True)
def test_verifier(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_errors_section_data():
    return {
        'verifier': {
            'name': int(),
            'enabled': str(),
            'directory': int(),
            'options': [],
            'env': {
                'foo': 'foo',
                'foo-bar': 'foo-bar',
            },
            'additional_files_or_dirs': [
                int(),
            ],
            'lint': {
                'name': int(),
                'enabled': str(),
                'options': [],
                'env': {
                    'foo': 'foo',
                    'foo-bar': 'foo-bar',
                },
            },
        }
    }


@pytest.mark.parametrize(
    '_config', ['_model_verifier_errors_section_data'], indirect=True)
def test_verifier_has_errors(_config):
    x = {
        'verifier': [{
            'name': ['must be of string type'],
            'lint': [{
                'enabled': ['must be of boolean type'],
                'name': ['must be of string type'],
                'env': [{
                    'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                    'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
                }],
                'options': ['must be of dict type'],
            }],
            'enabled': ['must be of boolean type'],
            'env': [{
                'foo': ["value does not match regex '^[A-Z0-9_-]+$'"],
                'foo-bar': ["value does not match regex '^[A-Z0-9_-]+$'"],
            }],
            'directory': ['must be of string type'],
            'additional_files_or_dirs': [{
                0: ['must be of string type'],
            }],
            'options': ['must be of dict type'],
        }]
    }

    assert x == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_allows_testinfra_section_data():
    return {
        'verifier': {
            'name': 'testinfra',
            'lint': {
                'name': 'flake8',
            },
        }
    }


@pytest.fixture
def _model_verifier_allows_inspec_section_data():
    return {
        'verifier': {
            'name': 'inspec',
            'lint': {
                'name': 'rubocop',
            },
        }
    }


@pytest.fixture
def _model_verifier_allows_ansible_section_data():
    return {
        'verifier': {
            'name': 'ansible',
            'lint': {
                'name': 'ansible-lint',
            },
        }
    }


@pytest.fixture
def _model_verifier_allows_goss_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'lint': {
                'name': 'yamllint',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', [
        ('_model_verifier_allows_testinfra_section_data'),
        ('_model_verifier_allows_inspec_section_data'),
        ('_model_verifier_allows_goss_section_data'),
        ('_model_verifier_allows_ansible_section_data'),
    ],
    indirect=True)
def test_verifier_allows_name(_config):
    assert {} == schema_v2.validate(_config)


@pytest.fixture
def _model_verifier_errors_inspec_readonly_options_section_data():
    return {
        'verifier': {
            'name': 'inspec',
            'options': {
                'foo': 'bar',
            },
            'lint': {
                'name': 'rubocop',
            },
        }
    }


@pytest.fixture
def _model_verifier_errors_goss_readonly_options_section_data():
    return {
        'verifier': {
            'name': 'goss',
            'options': {
                'foo': 'bar',
            },
            'lint': {
                'name': 'yamllint',
            },
        }
    }


@pytest.mark.parametrize(
    '_config', [
        ('_model_verifier_errors_inspec_readonly_options_section_data'),
        ('_model_verifier_errors_goss_readonly_options_section_data'),
    ],
    indirect=True)
def test_verifier_errors_readonly_options_section_data(_config):
    x = {'verifier': [{'options': [{'foo': ['field is read-only']}]}]}

    assert x == schema_v2.validate(_config)
