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

from typing import TYPE_CHECKING

from molecule.model import schema_v3
from molecule.util import run_command


if TYPE_CHECKING:
    from pathlib import Path


def test_base_config(config):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    assert not schema_v3.validate(config)


def test_molecule_schema(resources_folder_path: Path) -> None:
    """Test the molecule schema.

    Args:
        resources_folder_path: Path to the resources folder.
    """
    cmd = [
        "check-jsonschema",
        "-v",
        "--schemafile",
        "src/molecule/data/molecule.json",
        f"{resources_folder_path}/schema_instance_files/valid/molecule.yml",
    ]
    assert run_command(cmd).returncode == 0

    cmd = [
        "check-jsonschema",
        "-v",
        "--schemafile",
        "src/molecule/data/driver.json",
        f"{resources_folder_path}/schema_instance_files/invalid/molecule_delegated.yml",
    ]
    assert run_command(cmd).returncode != 0
