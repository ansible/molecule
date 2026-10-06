"""Regression tests for schema validation diagnostics."""

from __future__ import annotations

import json

from typing import TYPE_CHECKING, Any, cast

import pytest

from molecule.model import schema_v3


if TYPE_CHECKING:
    from pathlib import Path

    from molecule.types import ConfigData


@pytest.mark.parametrize(
    ("instance", "expected"),
    (
        (
            {"platforms": [{"cgroupns": "host"}]},
            "$.platforms[0]: Additional properties are not allowed ('cgroupns' was unexpected)",
        ),
        (
            {"platforms": [{}, {"privileged": "yes"}]},
            "$.platforms[1].privileged: 'yes' is not of type 'boolean'",
        ),
        ({}, "$: 'platforms' is a required property"),
        ({"platforms": [{"privileged": True}]}, None),
    ),
)
def test_validation_error_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    instance: dict[str, Any],
    expected: str | None,
) -> None:
    """Report the location of schema errors, including driver platform errors.

    Args:
        tmp_path: Temporary directory for the driver schema.
        monkeypatch: Fixture for selecting the test schema.
        instance: Configuration to validate.
        expected: Expected error, or None for valid configuration.
    """
    schema = {
        "type": "object",
        "required": ["platforms"],
        "properties": {
            "platforms": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"privileged": {"type": "boolean"}},
                },
            },
        },
    }
    schema_file = tmp_path / "driver.json"
    schema_file.write_text(json.dumps(schema), encoding="utf-8")
    monkeypatch.setattr(schema_v3, "_collect_schema_files", lambda _: [str(schema_file)])

    assert schema_v3.validate(cast("ConfigData", instance)) == (
        [] if expected is None else [expected]
    )


@pytest.mark.parametrize("name", ("invalid-driver", 42))
def test_driver_name_error_preserved(name: str | int) -> None:
    """Keep the custom driver-name diagnostic.

    Args:
        name: Invalid driver name to validate.
    """
    errors = schema_v3.validate(cast("ConfigData", {"driver": {"name": name}, "platforms": []}))

    assert len(errors) == 1
    assert errors[0].startswith(f"{name!r} is not one of [")
    assert "$.driver.name" not in errors[0]
