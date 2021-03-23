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
"""Unittest for v2 config format."""

import os

import pytest

from molecule import util


@pytest.fixture
def _molecule_file():
    return os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
        os.path.pardir,
        "resources",
        "molecule.yml",
    )


@pytest.fixture
def _config(_molecule_file, request):
    with open(_molecule_file) as f:
        d = util.safe_load(f)
    if hasattr(request, "param"):
        if isinstance(request.getfixturevalue(request.param), str):
            d2 = util.safe_load(request.getfixturevalue(request.param))
        else:
            d2 = request.getfixturevalue(request.param)
        # print(100, d)
        # print(200, d2)
        d = util.merge_dicts(d, d2)
        # print(300, d)

    return d


@pytest.fixture
def _model_platforms_delegated_section_data():
    return """
---
platforms:
  - name: instance
""".strip()
