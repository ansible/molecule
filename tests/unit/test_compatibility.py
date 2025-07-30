# mypy: ignore-errors
"""Test the molecule compatibility module."""

from __future__ import annotations

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

    # Use _generate_next_value_ directly to test auto() behavior
    RED = StrEnum._generate_next_value_("RED", 1, 0, [])
    GREEN = StrEnum._generate_next_value_("GREEN", 1, 1, ["red"])
    BLUE = StrEnum._generate_next_value_("BLUE", 1, 2, ["red", "green"])


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
    assert f"{CompatEnum.FOO:>10}" == "       foo"


def test_str_enum_auto_behavior() -> None:
    """Test that auto() produces lowercase member names."""
    # Both implementations should produce lowercase names
    assert AutoEnum.RED == "red"
    assert AutoEnum.GREEN == "green"
    assert AutoEnum.BLUE == "blue"


def test_str_enum_repr() -> None:
    """Test StrEnum representation."""
    # Consistent repr format with vendored implementation
    assert "CompatEnum.FOO" in repr(CompatEnum.FOO)
    assert "foo" in repr(CompatEnum.FOO)


def test_str_enum_iteration() -> None:
    """Test that StrEnum can be iterated."""
    members = list(CompatEnum)
    assert len(members) == EXPECTED_ENUM_COUNT
    assert CompatEnum.FOO in members
    assert CompatEnum.BAR in members
    assert CompatEnum.BAZ_QUX in members


def test_str_enum_comparison() -> None:
    """Test StrEnum string comparison."""
    assert CompatEnum.FOO == "foo"
    assert CompatEnum.BAR != "foo"
    assert CompatEnum.BAZ_QUX == "baz_qux"


def test_str_enum_compatibility() -> None:
    """Test that StrEnum has consistent behavior."""
    # Verify the enum works as expected
    test_enum = CompatEnum.FOO
    assert isinstance(test_enum, str)
    assert isinstance(test_enum, CompatEnum)
    assert str(test_enum) == "foo"

    # No custom methods should be present
    assert not hasattr(CompatEnum, "list")
    assert not hasattr(CompatEnum, "from_str")


def test_str_enum_hash_behavior() -> None:
    """Test StrEnum hash behavior for use in sets/dicts."""
    enum_set = {CompatEnum.FOO, CompatEnum.BAR, CompatEnum.FOO}
    assert len(enum_set) == EXPECTED_UNIQUE_SET_SIZE  # Duplicates should be removed

    enum_dict = {CompatEnum.FOO: "value1", CompatEnum.BAR: "value2"}
    assert enum_dict[CompatEnum.FOO] == "value1"
    assert enum_dict[CompatEnum.BAR] == "value2"


def test_str_enum_basic_functionality() -> None:
    """Test core StrEnum functionality."""
    # Test that it's both a string and an enum
    assert isinstance(CompatEnum.FOO, str)
    assert isinstance(CompatEnum.FOO, CompatEnum)

    # Test string operations
    assert CompatEnum.FOO.upper() == "FOO"
    assert CompatEnum.FOO.replace("o", "x") == "fxx"

    # Test enum operations
    assert CompatEnum.FOO.name == "FOO"
    assert CompatEnum.FOO.value == "foo"


def test_str_enum_string_methods() -> None:
    """Test that string methods work correctly on StrEnum."""
    # Test various string methods work
    assert CompatEnum.FOO.startswith("f")
    assert CompatEnum.BAR.endswith("r")
    assert CompatEnum.FOO.capitalize() == "Foo"
    assert CompatEnum.BAR.count("a") == 1

    # Test string formatting
    assert f"prefix_{CompatEnum.FOO}_suffix" == "prefix_foo_suffix"
    assert CompatEnum.FOO.center(10, "*") == "***foo****"


def test_str_enum_new_method() -> None:
    """Test StrEnum.__new__ behavior."""
    # Test that creating from string works correctly
    assert CompatEnum("foo") == CompatEnum.FOO
    assert CompatEnum("bar") == CompatEnum.BAR
