# Copyright (c) 2013-2021, Audrey Roy Greenfeld
# All rights reserved.

# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:

# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Taken from Cookiecutter:
# https://github.com/cookiecutter/cookiecutter/blob/master/tests/test_generate_files.py
"""Tests for `generate_files` function and related errors raising.

Use the global clean_system fixture and run additional teardown code to remove
some special folders.
"""
from pathlib import Path

import pytest

from molecule import exceptions, generate


def test_generate_files_nontemplated_exception(tmp_path):
    """
    Verify `generate_files` raises when no directories to render exist.

    Note: Check `src/molecule/test/unit/test-generate-files-nontemplated` location to understand.
    """
    with pytest.raises(exceptions.NonTemplatedInputDirException):
        generate.generate_files(
            context={"cookiecutter": {"food": "pizza"}},
            repo_dir="src/molecule/test/unit/test-generate-files-nontemplated",
            output_dir=tmp_path,
        )


def test_generate_files(tmp_path):
    """Verify directory name correctly rendered with unicode containing context."""
    generate.generate_files(
        context={"cookiecutter": {"food": "pizzä"}},
        repo_dir="src/molecule/test/unit/test-generate-files",
        output_dir=tmp_path,
    )

    simple_file = Path(tmp_path, "inputpizzä/simple.txt")
    assert simple_file.exists()
    assert simple_file.is_file()

    with open(simple_file, "rt", encoding="utf-8") as f:
        simple_text = f.read()
    assert simple_text == "I eat pizzä\n"


def test_generate_files_with_linux_newline(tmp_path):
    """Verify new line not removed by templating engine after folder generation."""
    generate.generate_files(
        context={"cookiecutter": {"food": "pizzä"}},
        repo_dir="src/molecule/test/unit/test-generate-files",
        output_dir=tmp_path,
    )

    newline_file = Path(tmp_path, "inputpizzä/simple-with-newline.txt")
    assert newline_file.is_file()
    assert newline_file.exists()

    with open(newline_file, "r", encoding="utf-8", newline="") as f:
        simple_text = f.readline()
    assert simple_text == "newline is LF\n"
    assert f.newlines == "\n"


def test_generate_files_with_trailing_newline_forced_to_linux_by_context(tmp_path):
    """Verify new line not removed by templating engine after folder generation."""
    generate.generate_files(
        context={"cookiecutter": {"food": "pizzä", "_new_lines": "\r\n"}},
        repo_dir="src/molecule/test/unit/test-generate-files",
        output_dir=tmp_path,
    )

    # assert 'Overwritting endline character with %s' in caplog.messages
    newline_file = Path(tmp_path, "inputpizzä/simple-with-newline.txt")
    assert newline_file.is_file()
    assert newline_file.exists()

    with open(newline_file, "r", encoding="utf-8", newline="") as f:
        simple_text = f.readline()
    assert simple_text == "newline is LF\r\n"
    assert f.newlines == "\r\n"


def test_generate_files_absolute_path(tmp_path):
    """Verify usage of absolute path does not change files generation behaviour."""
    generate.generate_files(
        context={"cookiecutter": {"food": "pizzä"}},
        repo_dir=Path("src/molecule/test/unit/test-generate-files").absolute(),
        output_dir=tmp_path,
    )
    assert Path(tmp_path, "inputpizzä/simple.txt").is_file()


def test_generate_files_output_dir(tmp_path):
    """Verify `output_dir` option for `generate_files` changing location correctly."""
    output_dir = Path(tmp_path, "custom_output_dir")
    output_dir.mkdir()

    project_dir = generate.generate_files(
        context={"cookiecutter": {"food": "pizzä"}},
        repo_dir=Path("src/molecule/test/unit/test-generate-files").absolute(),
        output_dir=output_dir,
    )

    assert Path(output_dir, "inputpizzä/simple.txt").exists()
    assert Path(output_dir, "inputpizzä/simple.txt").is_file()
    assert Path(project_dir) == Path(tmp_path, "custom_output_dir/inputpizzä")


@pytest.fixture
def output_dir(tmp_path):
    """Fixture to prepare test output directory."""
    output_path = tmp_path.joinpath("output")
    output_path.mkdir()
    return str(output_path)


@pytest.fixture
def undefined_context():
    """Fixture. Populate context variable for future tests."""
    return {
        "cookiecutter": {"project_slug": "testproject", "github_username": "hackebrot"}
    }


def test_raise_undefined_variable_file_name(output_dir, undefined_context):
    """Verify correct error raised when file name cannot be rendered."""
    # https://github.com/prettier/prettier/issues/12143
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir="src/molecule/test/unit/undefined-variable/file-name/",
            output_dir=output_dir,
            context=undefined_context,
        )
    error = err.value
    assert "Unable to create file '{{cookiecutter.foobar}}.rst'" == error.message
    assert error.context == undefined_context

    assert not Path(output_dir).joinpath("testproject").exists()


def test_raise_undefined_variable_file_name_existing_project(
    output_dir, undefined_context
):
    """Verify correct error raised when file name cannot be rendered."""
    testproj_path = Path(output_dir, "testproject")
    testproj_path.mkdir()

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir="src/molecule/test/unit/undefined-variable/file-name/",
            output_dir=output_dir,
            context=undefined_context,
        )
    error = err.value
    assert "Unable to create file '{{cookiecutter.foobar}}.rst'" == error.message
    assert error.context == undefined_context

    assert testproj_path.exists()


def test_raise_undefined_variable_file_content(output_dir, undefined_context):
    """Verify correct error raised when file content cannot be rendered."""
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir="src/molecule/test/unit/undefined-variable/file-content/",
            output_dir=output_dir,
            context=undefined_context,
        )
    error = err.value
    assert "Unable to create file 'README.rst'" == error.message
    assert error.context == undefined_context

    assert not Path(output_dir).joinpath("testproject").exists()


def test_raise_undefined_variable_dir_name(output_dir, undefined_context):
    """Verify correct error raised when directory name cannot be rendered."""
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir="src/molecule/test/unit/undefined-variable/dir-name/",
            output_dir=output_dir,
            context=undefined_context,
        )
    error = err.value

    directory = Path("testproject", "{{cookiecutter.foobar}}")
    msg = f"Unable to create directory '{directory}'"
    assert msg == error.message

    assert error.context == undefined_context

    assert not Path(output_dir).joinpath("testproject").exists()


def test_raise_undefined_variable_dir_name_existing_project(
    output_dir, undefined_context
):
    """Verify correct error raised when directory name cannot be rendered."""
    testproj_path = Path(output_dir, "testproject")
    testproj_path.mkdir()

    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir="src/molecule/test/unit/undefined-variable/dir-name/",
            output_dir=output_dir,
            context=undefined_context,
        )
    error = err.value

    directory = Path("testproject", "{{cookiecutter.foobar}}")
    msg = f"Unable to create directory '{directory}'"
    assert msg == error.message

    assert error.context == undefined_context

    assert testproj_path.exists()


def test_raise_undefined_variable_project_dir(tmp_path):
    """Verify correct error raised when directory name cannot be rendered."""
    with pytest.raises(exceptions.UndefinedVariableInTemplate) as err:
        generate.generate_files(
            repo_dir="src/molecule/test/unit/undefined-variable/dir-name/",
            output_dir=tmp_path,
            context={},
        )
    error = err.value
    msg = "Unable to create project directory '{{cookiecutter.project_slug}}'"
    assert msg == error.message
    assert error.context == {}

    assert not Path(tmp_path, "testproject").exists()
