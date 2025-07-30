"""Test the molecule compatibility module."""

from __future__ import annotations

from molecule.compatibility import StrEnum


# Test constants
EXPECTED_ENUM_COUNT = 3
EXPECTED_UNIQUE_SET_SIZE = 2


class TestCompatEnum(StrEnum):  # noqa: DOC601, DOC603
    """Test enum for compatibility testing."""

    FOO = "foo"
    BAR = "bar"
    BAZ_QUX = "baz_qux"


class TestAutoEnum(StrEnum):  # noqa: DOC601, DOC603
    """Test enum using auto() for compatibility testing."""

    # Use _generate_next_value_ directly to test auto() behavior
    RED = StrEnum._generate_next_value_("RED", 1, 0, [])
    GREEN = StrEnum._generate_next_value_("GREEN", 1, 1, ["red"])
    BLUE = StrEnum._generate_next_value_("BLUE", 1, 2, ["red", "green"])


def test_str_enum_string_behavior() -> None:
    """Test that StrEnum behaves like a string."""
    assert str(TestCompatEnum.FOO) == "foo"
    assert TestCompatEnum.FOO == "foo"
    assert TestCompatEnum.BAR == "bar"
    assert TestCompatEnum.BAZ_QUX == "baz_qux"


def test_str_enum_format_behavior() -> None:
    """Test StrEnum format behavior matches Python 3.11."""
    # Test __str__ behavior
    assert str(TestCompatEnum.FOO) == "foo"

    # Test __format__ behavior
    assert f"{TestCompatEnum.FOO}" == "foo"
    assert f"{TestCompatEnum.FOO:>10}" == "       foo"


def test_str_enum_auto_behavior() -> None:
    """Test that auto() produces lowercase member names."""
    # Both implementations should produce lowercase names
    assert TestAutoEnum.RED == "red"
    assert TestAutoEnum.GREEN == "green"
    assert TestAutoEnum.BLUE == "blue"


def test_str_enum_repr() -> None:
    """Test StrEnum representation."""
    # Consistent repr format with vendored implementation
    assert "TestCompatEnum.FOO" in repr(TestCompatEnum.FOO)
    assert "foo" in repr(TestCompatEnum.FOO)


def test_str_enum_iteration() -> None:
    """Test that StrEnum can be iterated."""
    members = list(TestCompatEnum)
    assert len(members) == EXPECTED_ENUM_COUNT
    assert TestCompatEnum.FOO in members
    assert TestCompatEnum.BAR in members
    assert TestCompatEnum.BAZ_QUX in members


def test_str_enum_comparison() -> None:
    """Test StrEnum string comparison."""
    assert TestCompatEnum.FOO == "foo"
    assert TestCompatEnum.BAR != "foo"
    assert TestCompatEnum.BAZ_QUX == "baz_qux"


def test_str_enum_compatibility() -> None:
    """Test that StrEnum has consistent behavior."""
    # Verify the enum works as expected
    test_enum = TestCompatEnum.FOO
    assert isinstance(test_enum, str)
    assert isinstance(test_enum, TestCompatEnum)
    assert str(test_enum) == "foo"

    # No custom methods should be present
    assert not hasattr(TestCompatEnum, "list")
    assert not hasattr(TestCompatEnum, "from_str")


def test_str_enum_hash_behavior() -> None:
    """Test StrEnum hash behavior for use in sets/dicts."""
    enum_set = {TestCompatEnum.FOO, TestCompatEnum.BAR, TestCompatEnum.FOO}
    assert len(enum_set) == EXPECTED_UNIQUE_SET_SIZE  # Duplicates should be removed

    enum_dict = {TestCompatEnum.FOO: "value1", TestCompatEnum.BAR: "value2"}
    assert enum_dict[TestCompatEnum.FOO] == "value1"
    assert enum_dict[TestCompatEnum.BAR] == "value2"


def test_str_enum_basic_functionality() -> None:
    """Test core StrEnum functionality."""
    # Test that it's both a string and an enum
    assert isinstance(TestCompatEnum.FOO, str)
    assert isinstance(TestCompatEnum.FOO, TestCompatEnum)

    # Test string operations
    assert TestCompatEnum.FOO.upper() == "FOO"
    assert TestCompatEnum.FOO.replace("o", "x") == "fxx"

    # Test enum operations
    assert TestCompatEnum.FOO.name == "FOO"
    assert TestCompatEnum.FOO.value == "foo"


def test_str_enum_string_methods() -> None:
    """Test that string methods work correctly on StrEnum."""
    # Test various string methods work
    assert TestCompatEnum.FOO.startswith("f")
    assert TestCompatEnum.BAR.endswith("r")
    assert TestCompatEnum.FOO.capitalize() == "Foo"
    assert TestCompatEnum.BAR.count("a") == 1

    # Test string formatting
    assert f"prefix_{TestCompatEnum.FOO}_suffix" == "prefix_foo_suffix"
    assert TestCompatEnum.FOO.center(10, "*") == "***foo****"


def test_str_enum_new_method() -> None:
    """Test StrEnum.__new__ behavior."""
    # Test that creating from string works correctly
    assert TestCompatEnum("foo") == TestCompatEnum.FOO
    assert TestCompatEnum("bar") == TestCompatEnum.BAR
