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
