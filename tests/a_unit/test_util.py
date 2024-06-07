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


import binascii
import os
import warnings

from pathlib import Path
from typing import Any

import pytest

from molecule import util
from molecule.api import IncompatibleMoleculeRuntimeWarning, MoleculeRuntimeWarning
from molecule.console import console
from molecule.constants import MOLECULE_HEADER
from molecule.text import strip_ansi_escape
from pytest_mock import MockerFixture

from tests.conftest import (  # pylint:disable = C0411
    get_molecule_file,
    molecule_directory,
)


def test_print_debug():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    expected = "DEBUG: test_title:\ntest_data\n"
    with console.capture() as capture:
        util.print_debug("test_title", "test_data")

    result = strip_ansi_escape(capture.get())  # type: ignore[no-untyped-call]
    assert result == expected


def test_print_environment_vars(capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG001, D103
    env = {
        "ANSIBLE_FOO": "foo",
        "ANSIBLE_BAR": "bar",
        "ANSIBLE": None,
        "MOLECULE_FOO": "foo",
        "MOLECULE_BAR": "bar",
        "MOLECULE": None,
    }
    expected = """DEBUG: ANSIBLE ENVIRONMENT:
ANSIBLE_BAR: bar
ANSIBLE_FOO: foo

DEBUG: MOLECULE ENVIRONMENT:
MOLECULE_BAR: bar
MOLECULE_FOO: foo

DEBUG: SHELL REPLAY:
ANSIBLE_BAR=bar ANSIBLE_FOO=foo MOLECULE_BAR=bar MOLECULE_FOO=foo
"""

    with console.capture() as capture:
        util.print_environment_vars(env)
    result = strip_ansi_escape(capture.get())  # type: ignore[no-untyped-call]
    assert result == expected


def test_sysexit():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(SystemExit) as e:
        util.sysexit()

    assert e.value.code == 1


def test_sysexit_with_custom_code():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(SystemExit) as e:
        util.sysexit(2)

    assert e.value.code == 2  # noqa: PLR2004


def test_sysexit_with_message(caplog: pytest.LogCaptureFixture):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message("foo")

    assert e.value.code == 1

    assert "foo" in caplog.text


def test_sysexit_with_warns(caplog: pytest.LogCaptureFixture):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(SystemExit) as e:  # noqa: PT012
        with warnings.catch_warnings(record=True) as warns:
            warnings.filterwarnings("default", category=MoleculeRuntimeWarning)
            warnings.warn("xxx", category=IncompatibleMoleculeRuntimeWarning)  # noqa: B028

        util.sysexit_with_message("foo", warns=warns)

    assert e.value.code == 1

    assert "foo" in caplog.text
    assert "xxx" in caplog.text


def test_sysexit_with_message_and_custom_code(caplog: pytest.LogCaptureFixture):  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message("foo", 2)

    assert e.value.code == 2  # noqa: PLR2004

    assert "foo" in caplog.text


def test_run_command():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    cmd = ["ls"]
    x = util.run_command(cmd)

    assert x.returncode == 0


def test_run_command_with_debug(mocker: MockerFixture, patched_print_debug):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    env = {"ANSIBLE_FOO": "foo", "MOLECULE_BAR": "bar"}
    util.run_command(["ls"], debug=True, env=env)
    x = [
        mocker.call("ANSIBLE ENVIRONMENT", "ANSIBLE_FOO: foo\n"),
        mocker.call("MOLECULE ENVIRONMENT", "MOLECULE_BAR: bar\n"),
        mocker.call("SHELL REPLAY", "ANSIBLE_FOO=foo MOLECULE_BAR=bar"),
    ]

    assert x == patched_print_debug.mock_calls


def test_run_command_baked_cmd_env():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    cmd = ["printenv", "myvar"]
    result = util.run_command(cmd, env={"myvar": "value2"})
    assert result.returncode == 0

    cmd = ["printenv", "myvar2"]
    result = util.run_command(cmd, env={"myvar2": "value2"})
    assert result.returncode == 0

    # negative test
    cmd = ["printenv", "myvar"]
    result = util.run_command(cmd)
    assert result.returncode == 1


def test_run_command_with_debug_handles_no_env(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    mocker: MockerFixture,  # noqa: ARG001
    patched_print_debug,  # noqa: ANN001
):
    cmd = ["ls"]
    util.run_command(cmd, debug=True)
    # when env is empty we expect not to print anything
    empty_list: list[Any] = []

    assert empty_list == patched_print_debug.mock_calls


def test_os_walk(temp_dir):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    scenarios = ["scenario1", "scenario2", "scenario3"]
    mol_dir = molecule_directory()
    for scenario in scenarios:
        scenario_directory = os.path.join(mol_dir, scenario)  # noqa: PTH118
        molecule_file = get_molecule_file(scenario_directory)
        os.makedirs(scenario_directory, exist_ok=True)  # noqa: PTH103
        util.write_file(molecule_file, "")

    result = list(util.os_walk(mol_dir, "molecule.yml"))  # type: ignore[no-untyped-call]
    assert len(result) == 3  # noqa: PLR2004


def test_render_template():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    template = "{{ foo }} = {{ bar }}"

    assert util.render_template(template, foo="foo", bar="bar") == "foo = bar"  # type: ignore[no-untyped-call]


def test_render_template_quoted():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    template = """
    {{ 'url = "quoted_str"' }}
    """.strip()

    assert util.render_template(template) == 'url = "quoted_str"'  # type: ignore[no-untyped-call]


def test_write_file(temp_dir):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    dest_file = os.path.join(temp_dir.strpath, "test_util_write_file.tmp")  # noqa: PTH118
    contents = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    util.write_file(dest_file, contents)
    with open(dest_file) as stream:  # noqa: PTH123
        data = stream.read()
    x = f"# Molecule managed\n\n{contents}"

    assert x == data


def test_molecule_prepender(tmp_path: Path) -> None:  # noqa: D103
    fname = tmp_path / "some.txt"
    fname.write_text("foo bar")
    x = f"{MOLECULE_HEADER}\n\nfoo bar"
    util.file_prepender(str(fname))
    assert x == fname.read_text()


def test_safe_dump():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    x = """
---
foo: bar
""".lstrip()

    assert x == util.safe_dump({"foo": "bar"})


def test_safe_dump_with_increase_indent():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    data = {"foo": [{"foo": "bar", "baz": "zzyzx"}]}

    x = """
---
foo:
  - baz: zzyzx
    foo: bar
""".lstrip()
    assert x == util.safe_dump(data)


def test_safe_load() -> None:  # noqa: D103
    assert {"foo": "bar"} == util.safe_load("foo: bar")


def test_safe_load_returns_empty_dict_on_empty_string() -> None:  # noqa: D103
    assert {} == util.safe_load("")


def test_safe_load_exits_when_cannot_parse() -> None:  # noqa: D103
    data = """
---
%foo:
""".strip()

    with pytest.raises(SystemExit) as e:
        util.safe_load(data)

    assert e.value.code == 1


def test_safe_load_file(temp_dir) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, D103
    path = os.path.join(temp_dir.strpath, "foo")  # noqa: PTH118
    util.write_file(path, "foo: bar")

    assert {"foo": "bar"} == util.safe_load_file(path)


def test_instance_with_scenario_name() -> None:  # noqa: D103
    assert util.instance_with_scenario_name("foo", "bar") == "foo-bar"  # type: ignore[no-untyped-call]


def test_verbose_flag() -> None:  # noqa: D103
    options = {"verbose": True, "v": True}

    assert ["-v"] == util.verbose_flag(options)  # type: ignore[no-untyped-call]
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert {} == options


def test_verbose_flag_extra_verbose() -> None:  # noqa: D103
    options = {"verbose": True, "vvv": True}

    assert ["-vvv"] == util.verbose_flag(options)  # type: ignore[no-untyped-call]
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert {} == options


def test_verbose_flag_preserves_verbose_option() -> None:  # noqa: D103
    options = {"verbose": True}

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert [] == util.verbose_flag(options)  # type: ignore[no-untyped-call]
    assert {"verbose": True} == options


def test_filter_verbose_permutation() -> None:  # noqa: D103
    options = {
        "v": True,
        "vv": True,
        "vvv": True,
        "vfoo": True,
        "foo": True,
        "bar": True,
    }

    x = {"vfoo": True, "foo": True, "bar": True}
    assert x == util.filter_verbose_permutation(options)  # type: ignore[no-untyped-call]


def test_abs_path(temp_dir) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, ARG001, D103
    x = os.path.abspath(  # noqa: PTH100
        os.path.join(os.getcwd(), os.path.pardir, "foo", "bar"),  # noqa: PTH109, PTH118
    )

    assert x == util.abs_path(os.path.join(os.path.pardir, "foo", "bar"))  # noqa: PTH118


def test_abs_path_with_none_path() -> None:  # noqa: D103
    assert util.abs_path(None) is None  # type: ignore  # noqa: PGH003


@pytest.mark.parametrize(
    ("a", "b", "x"),
    [  # noqa: PT007
        # Base of recursion scenarios
        ({"key": 1}, {"key": 2}, {"key": 2}),
        ({"key": {}}, {"key": 2}, {"key": 2}),
        ({"key": 1}, {"key": {}}, {"key": {}}),
        # Recursive scenario
        ({"a": {"x": 1}}, {"a": {"x": 2}}, {"a": {"x": 2}}),
        ({"a": {"x": 1}}, {"a": {"y": 2}}, {"a": {"x": 1, "y": 2}}),
        # example taken from python-anyconfig/anyconfig/__init__.py
        (
            {"b": [{"c": 0}, {"c": 2}], "d": {"e": "aaa", "f": 3}},
            {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb"}},
            {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb", "f": 3}},
        ),
    ],
)
def test_merge_dicts(a, b, x) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, D103
    assert x == util.merge_dicts(a, b)
