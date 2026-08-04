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


@pytest.mark.parametrize(
    "config",
    ["_model_platforms_delegated_section_data"],  # noqa: PT007
    indirect=True,
)
def test_platforms_delegated(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    assert not schema_v3.validate(config)


@pytest.mark.parametrize(
    "config",
    ["_model_platforms_valid_relaxed_section_data"],  # noqa: PT007
    indirect=True,
)
def test_platforms_valid_relaxed(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # A fully-specified platform (name, groups, children as a list, a network
    # entry) with the relaxed command/cpus/memory types must validate cleanly.
    assert not schema_v3.validate(config)


@pytest.mark.parametrize(
    "config",
    ["_model_platforms_invalid_children_section_data"],  # noqa: PT007
    indirect=True,
)
def test_platforms_invalid_children(config):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # Guards the platforms.items $ref against regressing to an open object:
    # children must be a list, here an int (name set so it is the only fault).
    assert schema_v3.validate(config)
