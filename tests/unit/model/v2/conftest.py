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
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from molecule import util


if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


@pytest.fixture(name="molecule_file")
def fixture_molecule_file(resources_folder_path: Path) -> Path:
    """Return path to molecule file.

    Args:
        resources_folder_path: Path to the resources folder.

    Returns:
        Path to molecule file.
    """
    return resources_folder_path / "molecule.yml"


@pytest.fixture
def config(molecule_file: Path, request: pytest.FixtureRequest) -> dict[str, Any]:
    """Return merged molecule file data.

    Args:
        molecule_file: Path to molecule file.
        request: Pytest fixture request.

    Returns:
        Merged molecule file data.
    """
    with molecule_file.open() as f:
        d = util.safe_load(f)
    if hasattr(request, "param"):
        if isinstance(request.getfixturevalue(request.param), str):
            d2 = util.safe_load(request.getfixturevalue(request.param))
        else:
            d2 = request.getfixturevalue(request.param)
        d = util.merge_dicts(d, d2)

    return d  # type: ignore[no-any-return]


@pytest.fixture
def _model_platforms_delegated_section_data() -> str:
    return """
---
platforms:
  - name: instance
""".strip()
