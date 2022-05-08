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
# https://github.com/cookiecutter/cookiecutter/blob/master/tests/test_generate_file.py
"""Tests for `generate_file` function, part of `generate_files` function workflow."""
import os

import pytest
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError

from molecule import generate


@pytest.fixture(scope="function", autouse=True)
def tear_down():
    """
    Fixture. Remove the test text file which is created by the tests.

    Used for all tests in this file.
    """
    yield
    if os.path.exists("src/molecule/test/unit/files/cheese.txt"):
        os.remove("src/molecule/test/unit/files/cheese.txt")


@pytest.fixture
def env():
    """Fixture. Set Jinja2 environment settings for other tests."""
    environment = Environment()
    environment.loader = FileSystemLoader(".")
    return environment


def test_generate_file(env):
    """Verify simple file is generated with rendered context data."""
    infile = "src/molecule/test/unit/files/{{cookiecutter.generate_file}}.txt"
    generate.generate_file(
        project_dir=".",
        infile=infile,
        context={"cookiecutter": {"generate_file": "cheese"}},
        env=env,
    )
    assert os.path.isfile("src/molecule/test/unit/files/cheese.txt")
    with open("src/molecule/test/unit/files/cheese.txt", "rt") as f:
        generated_text = f.read()
        assert generated_text == "Testing cheese"


@pytest.fixture
def expected_msg():
    """Fixture. Used to ensure that exception generated text contain full data."""
    msg = (
        "Missing end of comment tag\n"
        '  File "src/molecule/test/unit/files/syntax_error.txt", line 1\n'
        "    I eat {{ syntax_error }} {# this comment is not closed}"
    )
    return msg.replace("/", os.sep)


def test_generate_file_verbose_template_syntax_error(env, expected_msg):
    """Verify correct exception raised on syntax error in file before generation."""
    with pytest.raises(TemplateSyntaxError) as exception:
        generate.generate_file(
            project_dir=".",
            infile="src/molecule/test/unit/files/syntax_error.txt",
            context={"syntax_error": "syntax_error"},
            env=env,
        )
    assert str(exception.value) == expected_msg
