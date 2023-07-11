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


import binascii
import os
import warnings
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from molecule import util
from molecule.api import IncompatibleMoleculeRuntimeWarning, MoleculeRuntimeWarning
from molecule.console import console
from molecule.constants import MOLECULE_HEADER
from molecule.test.conftest import get_molecule_file, molecule_directory
from molecule.text import strip_ansi_escape


def test_print_debug():
    expected = "DEBUG: test_title:\ntest_data\n"
    with console.capture() as capture:
        util.print_debug("test_title", "test_data")

    result = strip_ansi_escape(capture.get())
    assert result == expected


def test_print_environment_vars(capsys: pytest.CaptureFixture[str]) -> None:
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
    result = strip_ansi_escape(capture.get())
    assert result == expected


def test_sysexit():
    with pytest.raises(SystemExit) as e:
        util.sysexit()

    assert e.value.code == 1


def test_sysexit_with_custom_code():
    with pytest.raises(SystemExit) as e:
        util.sysexit(2)

    assert e.value.code == 2


def test_sysexit_with_message(caplog: pytest.LogCaptureFixture):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message("foo")

    assert e.value.code == 1

    assert "foo" in caplog.text


def test_sysexit_with_warns(caplog: pytest.LogCaptureFixture):
    with pytest.raises(SystemExit) as e:
        with warnings.catch_warnings(record=True) as warns:
            warnings.filterwarnings("default", category=MoleculeRuntimeWarning)
            warnings.warn("xxx", category=IncompatibleMoleculeRuntimeWarning)

        util.sysexit_with_message("foo", warns=warns)

    assert e.value.code == 1

    assert "foo" in caplog.text
    assert "xxx" in caplog.text


def test_sysexit_with_message_and_custom_code(caplog: pytest.LogCaptureFixture):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message("foo", 2)

    assert e.value.code == 2

    assert "foo" in caplog.text


def test_run_command():
    cmd = ["ls"]
    x = util.run_command(cmd)

    assert x.returncode == 0


def test_run_command_with_debug(mocker: MockerFixture, patched_print_debug):
    env = {"ANSIBLE_FOO": "foo", "MOLECULE_BAR": "bar"}
    util.run_command(["ls"], debug=True, env=env)
    x = [
        mocker.call("ANSIBLE ENVIRONMENT", "ANSIBLE_FOO: foo\n"),
        mocker.call("MOLECULE ENVIRONMENT", "MOLECULE_BAR: bar\n"),
        mocker.call("SHELL REPLAY", "ANSIBLE_FOO=foo MOLECULE_BAR=bar"),
    ]

    assert x == patched_print_debug.mock_calls


def test_run_command_baked_cmd_env():
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


def test_run_command_with_debug_handles_no_env(
    mocker: MockerFixture,
    patched_print_debug,
):
    cmd = ["ls"]
    util.run_command(cmd, debug=True)
    # when env is empty we expect not to print anything
    empty_list: list[Any] = []

    assert empty_list == patched_print_debug.mock_calls


def test_os_walk(temp_dir):
    scenarios = ["scenario1", "scenario2", "scenario3"]
    mol_dir = molecule_directory()
    for scenario in scenarios:
        scenario_directory = os.path.join(mol_dir, scenario)
        molecule_file = get_molecule_file(scenario_directory)
        os.makedirs(scenario_directory, exist_ok=True)
        util.write_file(molecule_file, "")

    result = list(util.os_walk(mol_dir, "molecule.yml"))
    assert len(result) == 3


def test_render_template():
    template = "{{ foo }} = {{ bar }}"

    assert util.render_template(template, foo="foo", bar="bar") == "foo = bar"


def test_render_template_quoted():
    template = """
    {{ 'url = "quoted_str"' }}
    """.strip()

    assert util.render_template(template) == 'url = "quoted_str"'


def test_write_file(temp_dir):
    dest_file = os.path.join(temp_dir.strpath, "test_util_write_file.tmp")
    contents = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    util.write_file(dest_file, contents)
    with open(dest_file) as stream:
        data = stream.read()
    x = f"# Molecule managed\n\n{contents}"

    assert x == data


def test_molecule_prepender(tmp_path: Path) -> None:
    fname = tmp_path / "some.txt"
    fname.write_text("foo bar")
    x = f"{MOLECULE_HEADER}\n\nfoo bar"
    util.file_prepender(str(fname))
    assert x == fname.read_text()


def test_safe_dump():
    x = """
---
foo: bar
""".lstrip()

    assert x == util.safe_dump({"foo": "bar"})


def test_safe_dump_with_increase_indent():
    data = {"foo": [{"foo": "bar", "baz": "zzyzx"}]}

    x = """
---
foo:
  - baz: zzyzx
    foo: bar
""".lstrip()
    assert x == util.safe_dump(data)


def test_safe_load() -> None:
    assert {"foo": "bar"} == util.safe_load("foo: bar")


def test_safe_load_returns_empty_dict_on_empty_string() -> None:
    assert {} == util.safe_load("")


def test_safe_load_exits_when_cannot_parse() -> None:
    data = """
---
%foo:
""".strip()

    with pytest.raises(SystemExit) as e:
        util.safe_load(data)

    assert e.value.code == 1


def test_safe_load_file(temp_dir) -> None:
    path = os.path.join(temp_dir.strpath, "foo")
    util.write_file(path, "foo: bar")

    assert {"foo": "bar"} == util.safe_load_file(path)


def test_instance_with_scenario_name() -> None:
    assert util.instance_with_scenario_name("foo", "bar") == "foo-bar"


def test_verbose_flag() -> None:
    options = {"verbose": True, "v": True}

    assert ["-v"] == util.verbose_flag(options)
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert {} == options


def test_verbose_flag_extra_verbose() -> None:
    options = {"verbose": True, "vvv": True}

    assert ["-vvv"] == util.verbose_flag(options)
    # pylint: disable=use-implicit-booleaness-not-comparison
    assert {} == options


def test_verbose_flag_preserves_verbose_option() -> None:
    options = {"verbose": True}

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert [] == util.verbose_flag(options)
    assert {"verbose": True} == options


def test_filter_verbose_permutation() -> None:
    options = {
        "v": True,
        "vv": True,
        "vvv": True,
        "vfoo": True,
        "foo": True,
        "bar": True,
    }

    x = {"vfoo": True, "foo": True, "bar": True}
    assert x == util.filter_verbose_permutation(options)


def test_abs_path(temp_dir) -> None:
    x = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir, "foo", "bar"))

    assert x == util.abs_path(os.path.join(os.path.pardir, "foo", "bar"))


def test_abs_path_with_none_path() -> None:
    assert util.abs_path(None) is None  # type: ignore


# pylint: disable=use-dict-literal
@pytest.mark.parametrize(
    ("a", "b", "x"),
    [
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
def test_merge_dicts(a, b, x) -> None:
    assert x == util.merge_dicts(a, b)
