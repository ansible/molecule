# mypy: ignore-errors
# pydoclint: disable
"""Test the molecule compatibility module."""

from __future__ import annotations

from enum import auto

from molecule.compatibility import StrEnum


# Test constants
EXPECTED_ENUM_COUNT = 3
EXPECTED_UNIQUE_SET_SIZE = 2


class CompatEnum(StrEnum):  # noqa: DOC601, DOC603
    """Test enum for compatibility testing."""

    FOO = "foo"
    BAR = "bar"
    BAZ_QUX = "baz_qux"


class AutoEnum(StrEnum):  # noqa: DOC601, DOC603
    """Test enum using auto() for compatibility testing."""

    RED = auto()
    GREEN = auto()
    BLUE = auto()


def test_str_enum_string_behavior() -> None:
    """Test that StrEnum behaves like a string."""
    assert str(CompatEnum.FOO) == "foo"
    assert CompatEnum.FOO == "foo"
    assert CompatEnum.BAR == "bar"
    assert CompatEnum.BAZ_QUX == "baz_qux"


def test_str_enum_format_behavior() -> None:
    """Test StrEnum format behavior matches Python 3.11."""
    # Test __str__ behavior
    assert str(CompatEnum.FOO) == "foo"

    # Test __format__ behavior
    assert f"{CompatEnum.FOO}" == "foo"
    assert f"{CompatEnum.BAR}" == "bar"
    assert f"{CompatEnum.BAZ_QUX}" == "baz_qux"

    # Test format with format spec
    assert f"{CompatEnum.FOO:>10}" == "       foo"
    assert f"{CompatEnum.BAR:<10}" == "bar       "


def test_str_enum_auto_behavior() -> None:
    """Test auto() behavior produces lowercase names."""
    assert AutoEnum.RED == "red"
    assert AutoEnum.GREEN == "green"
    assert AutoEnum.BLUE == "blue"


def test_str_enum_repr() -> None:
    """Test StrEnum repr behavior."""
    assert repr(CompatEnum.FOO) == "<CompatEnum.FOO: 'foo'>"
    assert repr(AutoEnum.RED) == "<AutoEnum.RED: 'red'>"


def test_str_enum_iteration() -> None:
    """Test StrEnum iteration."""
    values = [item.value for item in CompatEnum]
    assert len(values) == EXPECTED_ENUM_COUNT
    assert "foo" in values
    assert "bar" in values
    assert "baz_qux" in values


def test_str_enum_comparison() -> None:
    """Test StrEnum comparison with strings."""
    assert CompatEnum.FOO == "foo"
    assert CompatEnum.FOO != "bar"
    assert CompatEnum.BAR == "bar"
    assert CompatEnum.BAR != "foo"

    # Test with auto values
    assert AutoEnum.RED == "red"
    assert AutoEnum.GREEN == "green"


def test_str_enum_hash() -> None:
    """Test StrEnum hash behavior."""
    # Should be able to use as dict keys
    d = {CompatEnum.FOO: "value1", CompatEnum.BAR: "value2"}
    assert d[CompatEnum.FOO] == "value1"
    assert d[CompatEnum.BAR] == "value2"

    # Test uniqueness
    s = {CompatEnum.FOO, CompatEnum.BAR, CompatEnum.FOO}
    assert len(s) == EXPECTED_UNIQUE_SET_SIZE


def test_str_enum_basic_functionality() -> None:  # type: ignore
    """Test basic StrEnum functionality."""
    # Test membership
    assert CompatEnum.FOO in CompatEnum
    assert "random_value" not in [e.value for e in CompatEnum]

    # Test name access
    assert CompatEnum.FOO.name == "FOO"
    assert CompatEnum.BAR.name == "BAR"

    # Test value access
    assert CompatEnum.FOO.value == "foo"
    assert CompatEnum.BAR.value == "bar"


def test_str_enum_string_methods() -> None:
    """Test that string methods work on StrEnum."""
    assert CompatEnum.FOO.upper() == "FOO"
    assert CompatEnum.BAR.lower() == "bar"
    assert CompatEnum.FOO.capitalize() == "Foo"
    assert CompatEnum.BAZ_QUX.replace("_", "-") == "baz-qux"


def test_str_enum_new_method() -> None:  # type: ignore
    """Test StrEnum __new__ method behavior."""
    # Test creating with string value
    foo_enum = CompatEnum("foo")
    assert foo_enum == CompatEnum.FOO
    assert foo_enum is CompatEnum.FOO

    # Test that StrEnum converts non-string values to strings during enum creation
    class IntCompatEnum(StrEnum):
        ONE = 1  # This will be converted to "1" by StrEnum.__new__
        TWO = 2  # This will be converted to "2" by StrEnum.__new__

    # The actual values stored are strings
    assert IntCompatEnum.ONE.value == "1"
    assert IntCompatEnum.TWO.value == "2"

    # Lookup by the actual string value works
    assert IntCompatEnum("1") == IntCompatEnum.ONE
    assert IntCompatEnum("2") == IntCompatEnum.TWO
