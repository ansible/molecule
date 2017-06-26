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

import os

import marshmallow
import pytest

from molecule import util
from molecule.model import schema_v1


@pytest.fixture
def molecule_v1_file():
    return os.path.join(
        os.path.dirname(__file__), os.path.pardir, os.path.pardir, 'resources',
        'molecule_v1_vagrant.yml')


@pytest.fixture
def config(molecule_v1_file):
    return util.safe_load(open(molecule_v1_file))


def test_validate(config):
    data, errors = schema_v1.validate(config)

    assert {} == errors


def test_validate_raises_on_extra_field(config):
    config['driver']['extra'] = 'bar'

    with pytest.raises(marshmallow.ValidationError) as e:
        schema_v1.validate(config)

    assert 'Unknown field' in str(e)


def test_validate_raises_on_invalid_field(config):
    config['driver']['name'] = int

    with pytest.raises(marshmallow.ValidationError) as e:
        schema_v1.validate(config)

    assert 'Not a valid string.' in str(e)
