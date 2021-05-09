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

from __future__ import print_function

import binascii
import io
import os

import pytest

from molecule import util
from molecule.console import console
from molecule.constants import MOLECULE_HEADER
from molecule.text import strip_ansi_escape


def test_print_debug():

    expected = "DEBUG: test_title:\ntest_data\n"
    with console.capture() as capture:
        util.print_debug("test_title", "test_data")

    result = strip_ansi_escape(capture.get())
    assert result == expected


def test_print_environment_vars(capsys):
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

    assert 1 == e.value.code


def test_sysexit_with_custom_code():
    with pytest.raises(SystemExit) as e:
        util.sysexit(2)

    assert 2 == e.value.code


def test_sysexit_with_message(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message("foo")

    assert 1 == e.value.code

    patched_logger_critical.assert_called_once_with("foo")


def test_sysexit_with_message_and_custom_code(patched_logger_critical):
    with pytest.raises(SystemExit) as e:
        util.sysexit_with_message("foo", 2)

    assert 2 == e.value.code

    patched_logger_critical.assert_called_once_with("foo")


def test_run_command():
    cmd = ["ls"]
    x = util.run_command(cmd)

    assert 0 == x.returncode


def test_run_command_with_debug(mocker, patched_print_debug):
    env = {"ANSIBLE_FOO": "foo", "MOLECULE_BAR": "bar"}
    util.run_command(["ls"], debug=True, env=env)
    x = [
        mocker.call("ANSIBLE ENVIRONMENT", "ANSIBLE_FOO: foo\n"),
        mocker.call("MOLECULE ENVIRONMENT", "MOLECULE_BAR: bar\n"),
        mocker.call("SHELL REPLAY", "ANSIBLE_FOO=foo MOLECULE_BAR=bar"),
    ]

    assert x == patched_print_debug.mock_calls


def test_run_command_baked_env(mocker):
    run_mock = mocker.patch.object(util, "run")
    run_mock.return_value = mocker.Mock(returncode=0)
    cmd = util.BakedCommand(cmd=["ls"], env=None)

    util.run_command(cmd, env=dict(myvar="myrealvalue"))

    # call_args[1] contains kwargs
    assert run_mock.call_args[1]["env"] == dict(myvar="myrealvalue")


def test_run_command_baked_cmd_env(mocker):
    run_mock = mocker.patch.object(util, "run")
    run_mock.return_value = mocker.Mock(returncode=0)
    cmd = util.BakedCommand(cmd=["ls"], env=dict(myvar="myvalue"))

    util.run_command(cmd)

    # call_args[1] contains kwargs
    assert run_mock.call_args[1]["env"] == dict(myvar="myvalue")


def test_run_command_baked_both_envs(mocker):
    run_mock = mocker.patch.object(util, "run")
    run_mock.return_value = mocker.Mock(returncode=0)
    cmd = util.BakedCommand(cmd=["ls"], env=dict(myvar="myvalue"))

    util.run_command(cmd, env=dict(myvar="myrealvalue"))

    # call_args[1] contains kwargs
    assert run_mock.call_args[1]["env"] == dict(myvar="myrealvalue")


def test_run_command_with_debug_handles_no_env(mocker, patched_print_debug):
    cmd = "ls"
    util.run_command(cmd, debug=True)
    # when env is empty we expect not to print anything
    x = []

    assert x == patched_print_debug.mock_calls


def test_os_walk(temp_dir):
    scenarios = ["scenario1", "scenario2", "scenario3"]
    molecule_directory = pytest.helpers.molecule_directory()
    for scenario in scenarios:
        scenario_directory = os.path.join(molecule_directory, scenario)
        molecule_file = pytest.helpers.get_molecule_file(scenario_directory)
        os.makedirs(scenario_directory)
        util.write_file(molecule_file, "")

    result = [f for f in util.os_walk(molecule_directory, "molecule.yml")]
    assert 3 == len(result)


def test_render_template():
    template = "{{ foo }} = {{ bar }}"

    assert "foo = bar" == util.render_template(template, foo="foo", bar="bar")


def test_write_file(temp_dir):
    dest_file = os.path.join(temp_dir.strpath, "test_util_write_file.tmp")
    contents = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    util.write_file(dest_file, contents)
    with util.open_file(dest_file) as stream:
        data = stream.read()
    x = "# Molecule managed\n\n{}".format(contents)

    assert x == data


def molecule_prepender(content):
    x = f"{MOLECULE_HEADER}\nfoo bar"

    assert x == util.file_prepender("foo bar")


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


def test_safe_load():
    assert {"foo": "bar"} == util.safe_load("foo: bar")


def test_safe_load_returns_empty_dict_on_empty_string():
    assert {} == util.safe_load("")


def test_safe_load_exits_when_cannot_parse():
    data = """
---
%foo:
""".strip()

    with pytest.raises(SystemExit) as e:
        util.safe_load(data)

    assert 1 == e.value.code


def test_safe_load_file(temp_dir):
    path = os.path.join(temp_dir.strpath, "foo")
    util.write_file(path, "foo: bar")

    assert {"foo": "bar"} == util.safe_load_file(path)


def test_open_file(temp_dir):
    path = os.path.join(temp_dir.strpath, "foo")
    util.write_file(path, "foo: bar")

    with util.open_file(path) as stream:
        try:
            file_types = (file, io.IOBase)
        except NameError:
            file_types = io.IOBase

        assert isinstance(stream, file_types)


def test_instance_with_scenario_name():
    assert "foo-bar" == util.instance_with_scenario_name("foo", "bar")


def test_verbose_flag():
    options = {"verbose": True, "v": True}

    assert ["-v"] == util.verbose_flag(options)
    assert {} == options


def test_verbose_flag_extra_verbose():
    options = {"verbose": True, "vvv": True}

    assert ["-vvv"] == util.verbose_flag(options)
    assert {} == options


def test_verbose_flag_preserves_verbose_option():
    options = {"verbose": True}

    assert [] == util.verbose_flag(options)
    assert {"verbose": True} == options


def test_filter_verbose_permutation():
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


def test_abs_path(temp_dir):
    x = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir, "foo", "bar"))

    assert x == util.abs_path(os.path.join(os.path.pardir, "foo", "bar"))


def test_abs_path_with_none_path():
    assert util.abs_path(None) is None


@pytest.mark.parametrize(
    "a,b,x",
    [
        # Base of recursion scenarios
        (dict(key=1), dict(key=2), dict(key=2)),
        (dict(key={}), dict(key=2), dict(key=2)),
        (dict(key=1), dict(key={}), dict(key={})),
        # Recursive scenario
        (dict(a=dict(x=1)), dict(a=dict(x=2)), dict(a=dict(x=2))),
        (dict(a=dict(x=1)), dict(a=dict(y=2)), dict(a=dict(x=1, y=2))),
        # example taken from python-anyconfig/anyconfig/__init__.py
        (
            {"b": [{"c": 0}, {"c": 2}], "d": {"e": "aaa", "f": 3}},
            {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb"}},
            {"a": 1, "b": [{"c": 3}], "d": {"e": "bbb", "f": 3}},
        ),
    ],
)
def test_merge_dicts(a, b, x):
    assert x == util.merge_dicts(a, b)
