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

import pytest

from molecule import config, shell


if TYPE_CHECKING:
    from pathlib import Path


def test_shell() -> None:  # noqa: D103
    with pytest.raises(SystemExit):
        shell.main()  # pylint: disable=no-value-for-parameter


@pytest.mark.parametrize("extensions", ((), ("yml",), ("yaml",), ("yaml", "yml")))
def test_default_env_file_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extensions: tuple[str, ...],
) -> None:
    """Resolve the implicit env file in the invocation directory, not at import time.

    Args:
        tmp_path: Temporary invocation directory.
        monkeypatch: Fixture for changing working directory.
        extensions: Env files to create.
    """
    monkeypatch.chdir(tmp_path)
    for extension in extensions:
        (tmp_path / f".env.{extension}").write_text(f"MARKER: {extension}\n")
    with shell.main.make_context("molecule", ["list"]) as ctx:
        expected = ".env.yml" if "yml" in extensions or not extensions else ".env.yaml"
        assert ctx.params["env_file"] == expected
        env = config.set_env_from_file({}, expected)
        assert env == ({"MARKER": expected.rsplit(".", 1)[1]} if extensions else {})


@pytest.mark.parametrize("filename", ("custom.yml", "custom.yaml", ".env.yml"))
@pytest.mark.parametrize("available", ((), ("yml",), ("yaml",), ("yaml", "yml")))
def test_supplied_env_file_resolution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
    available: tuple[str, ...],
) -> None:
    """Supplied env files are exact even when they equal the default filename.

    Args:
        tmp_path: Temporary invocation directory.
        monkeypatch: Fixture for changing working directory.
        filename: Supplied env filename.
        available: Existing env file extensions.
    """
    monkeypatch.chdir(tmp_path)
    requested = tmp_path / filename
    for suffix in available:
        requested.with_suffix(f".{suffix}").write_text(f"MARKER: {suffix}\n")
    with shell.main.make_context("molecule", ["--env-file", filename, "list"]) as ctx:
        assert ctx.params["env_file"] == filename
        extension = requested.suffix[1:]
        expected = extension if extension in available else None
        assert config.set_env_from_file({}, filename) == ({"MARKER": expected} if expected else {})


def test_explicit_base_configs_preserve_order() -> None:
    """CLI base-config paths retain the supplied order."""
    with shell.main.make_context(
        "molecule",
        ["-c", "first.yaml", "-c", "second.yml", "list"],
    ) as ctx:
        assert ctx.params["base_config"] == ("first.yaml", "second.yml")
