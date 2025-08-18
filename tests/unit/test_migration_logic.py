"""Test migration logic for ansible configuration section."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast


if TYPE_CHECKING:
    from pathlib import Path

    import pytest

    from molecule.types import ConfigData

from molecule import config
from molecule.constants import DEFAULT_CONFIG
from molecule.model.schema_v3 import validate
from molecule.utils import util


# Constants for validation assertions
EXPECTED_ENV_OCCURRENCES = 2
EXPECTED_PLAYBOOKS_OCCURRENCES = 2


def create_config_object(config_data: dict[str, Any], tmp_path: Path) -> config.Config:
    """Create a Config object from test data using temporary directory.

    Args:
        config_data: The configuration data to write to the file.
        tmp_path: pytest tmp_path fixture for temporary directory.

    Returns:
        A Config object initialized with the test data.
    """
    # Create molecule directory structure
    molecule_dir = tmp_path / "molecule" / "default"
    molecule_dir.mkdir(parents=True, exist_ok=True)
    molecule_file = molecule_dir / "molecule.yml"

    # Write config data to file
    molecule_file.write_text(util.safe_dump(config_data))

    # Create Config object - this will trigger migration if needed
    return config.Config(str(molecule_file))


def test_ansible_args_migration(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test migration of ansible_args from provisioner to ansible.executor.args.ansible_playbook.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
        caplog: pytest LogCaptureFixture for capturing log messages.
    """
    # BEFORE: Config with legacy ansible_args in provisioner
    before_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "provisioner": {
            "name": "ansible",
            "ansible_args": ["--diff", "--check"],
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validate the before config
    validate(cast("ConfigData", before_config))

    # EXPECTED: Complete expected data structure after migration
    expected_final_config = {
        "ansible": {
            "cfg": {},
            "env": {},
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": [
                        "--diff",
                        "--check",
                    ],  # migrated from provisioner.ansible_args
                },
            },
            "playbooks": {
                "cleanup": "cleanup.yml",
                "create": "create.yml",
                "converge": "converge.yml",
                "destroy": "destroy.yml",
                "prepare": "prepare.yml",
                "side_effect": "side_effect.yml",
                "verify": "verify.yml",
            },
        },
        "dependency": DEFAULT_CONFIG["dependency"],  # not migrated
        "driver": DEFAULT_CONFIG["driver"],  # not migrated
        "platforms": [{"name": "instance"}],  # from user config
        "prerun": DEFAULT_CONFIG["prerun"],  # not migrated
        "role_name_check": DEFAULT_CONFIG["role_name_check"],  # not migrated
        "shared_state": DEFAULT_CONFIG["shared_state"],  # not migrated
        "provisioner": {
            "name": "ansible",
            # ansible_args removed - migrated to ansible.executor.args.ansible_playbook
            "connection_options": {},
            "options": {},
            "inventory": {
                "hosts": {},
                "host_vars": {},
                "group_vars": {},
                "links": {},
            },
            "children": {},
            "log": True,
        },
        "scenario": DEFAULT_CONFIG["scenario"],  # not migrated
        "verifier": DEFAULT_CONFIG["verifier"],  # not migrated
    }

    # Schema validate the expected structure
    validate(cast("ConfigData", expected_final_config))

    # Build expected log messages list
    expected_log_messages = []
    molecule_file = tmp_path / "molecule" / "default" / "molecule.yml"
    expected_log_messages.append(
        f"provisioner.ansible_args found in {molecule_file}, this can be defined in ansible.executor.args.ansible_playbook",
    )

    # Clear caplog and create config object
    caplog.clear()
    with caplog.at_level("DEBUG"):
        config_obj = create_config_object(before_config, tmp_path)

    # Compare migrated config to expected for equality
    assert config_obj.config == expected_final_config

    # Confirm DEBUG log statements exist for each migrated key
    for expected_log_message in expected_log_messages:
        assert any(expected_log_message in msg for msg in caplog.messages)


def test_config_options_migration(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test migration of config_options from provisioner to ansible.cfg.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
        caplog: pytest LogCaptureFixture for capturing log messages.
    """
    # BEFORE: Config with legacy config_options in provisioner
    before_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "provisioner": {
            "name": "ansible",
            "config_options": {
                "defaults": {"host_key_checking": False},
                "ssh_connection": {"pipelining": True},
            },
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validate the before config
    validate(cast("ConfigData", before_config))

    # EXPECTED: Complete expected data structure after migration
    expected_final_config = {
        "ansible": {
            "cfg": {
                "defaults": {
                    "host_key_checking": False,
                },  # migrated from provisioner.config_options
                "ssh_connection": {"pipelining": True},  # migrated from provisioner.config_options
            },
            "env": {},
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": [],
                },
            },
            "playbooks": {
                "cleanup": "cleanup.yml",
                "create": "create.yml",
                "converge": "converge.yml",
                "destroy": "destroy.yml",
                "prepare": "prepare.yml",
                "side_effect": "side_effect.yml",
                "verify": "verify.yml",
            },
        },
        "dependency": DEFAULT_CONFIG["dependency"],  # not migrated
        "driver": DEFAULT_CONFIG["driver"],  # not migrated
        "platforms": [{"name": "instance"}],  # from user config
        "prerun": DEFAULT_CONFIG["prerun"],  # not migrated
        "role_name_check": DEFAULT_CONFIG["role_name_check"],  # not migrated
        "shared_state": DEFAULT_CONFIG["shared_state"],  # not migrated
        "provisioner": {
            "name": "ansible",
            # config_options removed - migrated to ansible.cfg
            "connection_options": {},
            "options": {},
            "inventory": {
                "hosts": {},
                "host_vars": {},
                "group_vars": {},
                "links": {},
            },
            "children": {},
            "log": True,
        },
        "scenario": DEFAULT_CONFIG["scenario"],  # not migrated
        "verifier": DEFAULT_CONFIG["verifier"],  # not migrated
    }

    # Schema validate the expected structure
    validate(cast("ConfigData", expected_final_config))

    # Build expected log messages list
    expected_log_messages = []
    molecule_file = tmp_path / "molecule" / "default" / "molecule.yml"
    expected_log_messages.append(
        f"provisioner.config_options found in {molecule_file}, this can be defined in ansible.cfg",
    )

    # Clear caplog and create config object
    caplog.clear()
    with caplog.at_level("DEBUG"):
        config_obj = create_config_object(before_config, tmp_path)

    # Compare migrated config to expected for equality
    assert config_obj.config == expected_final_config

    # Confirm DEBUG log statements exist for each migrated key
    for expected_log_message in expected_log_messages:
        assert any(expected_log_message in msg for msg in caplog.messages)


def test_env_migration(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test migration of env from provisioner to ansible.env.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
        caplog: pytest LogCaptureFixture for capturing log messages.
    """
    # BEFORE: Config with legacy env in provisioner
    before_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "provisioner": {
            "name": "ansible",
            "env": {"ANSIBLE_VERBOSITY": "3", "ANSIBLE_HOST_KEY_CHECKING": "False"},
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validate the before config
    validate(cast("ConfigData", before_config))

    # EXPECTED: Complete expected data structure after migration
    expected_final_config = {
        "ansible": {
            "cfg": {},
            "env": {
                "ANSIBLE_VERBOSITY": "3",  # migrated from provisioner.env
                "ANSIBLE_HOST_KEY_CHECKING": "False",  # migrated from provisioner.env
            },
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": [],
                },
            },
            "playbooks": {
                "cleanup": "cleanup.yml",
                "create": "create.yml",
                "converge": "converge.yml",
                "destroy": "destroy.yml",
                "prepare": "prepare.yml",
                "side_effect": "side_effect.yml",
                "verify": "verify.yml",
            },
        },
        "dependency": DEFAULT_CONFIG["dependency"],  # not migrated
        "driver": DEFAULT_CONFIG["driver"],  # not migrated
        "platforms": [{"name": "instance"}],  # from user config
        "prerun": DEFAULT_CONFIG["prerun"],  # not migrated
        "role_name_check": DEFAULT_CONFIG["role_name_check"],  # not migrated
        "shared_state": DEFAULT_CONFIG["shared_state"],  # not migrated
        "provisioner": {
            "name": "ansible",
            # env removed - migrated to ansible.env
            "connection_options": {},
            "options": {},
            "inventory": {
                "hosts": {},
                "host_vars": {},
                "group_vars": {},
                "links": {},
            },
            "children": {},
            "log": True,
        },
        "scenario": DEFAULT_CONFIG["scenario"],  # not migrated
        "verifier": DEFAULT_CONFIG["verifier"],  # not migrated
    }

    # Schema validate the expected structure
    validate(cast("ConfigData", expected_final_config))

    # Build expected log messages list
    expected_log_messages = []
    molecule_file = tmp_path / "molecule" / "default" / "molecule.yml"
    expected_log_messages.append(
        f"provisioner.env found in {molecule_file}, this can be defined in ansible.env",
    )

    # Clear caplog and create config object
    caplog.clear()
    with caplog.at_level("DEBUG"):
        config_obj = create_config_object(before_config, tmp_path)

    # Compare migrated config to expected for equality
    assert config_obj.config == expected_final_config

    # Confirm DEBUG log statements exist for each migrated key
    for expected_log_message in expected_log_messages:
        assert any(expected_log_message in msg for msg in caplog.messages)


def test_playbooks_migration(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test migration of playbooks from provisioner to ansible.playbooks.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
        caplog: pytest LogCaptureFixture for capturing log messages.
    """
    # BEFORE: Config with legacy playbooks in provisioner
    before_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "provisioner": {
            "name": "ansible",
            "playbooks": {"converge": "my_converge.yml", "create": "my_create.yml"},
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validate the before config
    validate(cast("ConfigData", before_config))

    # EXPECTED: Complete expected data structure after migration (user values override defaults)
    expected_final_config = {
        "ansible": {
            "cfg": {},
            "env": {},
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": [],
                },
            },
            "playbooks": {
                "cleanup": "cleanup.yml",  # default preserved
                "create": "my_create.yml",  # user override from provisioner.playbooks
                "converge": "my_converge.yml",  # user override from provisioner.playbooks
                "destroy": "destroy.yml",  # default preserved
                "prepare": "prepare.yml",  # default preserved
                "side_effect": "side_effect.yml",  # default preserved
                "verify": "verify.yml",  # default preserved
            },
        },
        "dependency": DEFAULT_CONFIG["dependency"],  # not migrated
        "driver": DEFAULT_CONFIG["driver"],  # not migrated
        "platforms": [{"name": "instance"}],  # from user config
        "prerun": DEFAULT_CONFIG["prerun"],  # not migrated
        "role_name_check": DEFAULT_CONFIG["role_name_check"],  # not migrated
        "shared_state": DEFAULT_CONFIG["shared_state"],  # not migrated
        "provisioner": {
            "name": "ansible",
            # playbooks removed - migrated to ansible.playbooks
            "connection_options": {},
            "options": {},
            "inventory": {
                "hosts": {},
                "host_vars": {},
                "group_vars": {},
                "links": {},
            },
            "children": {},
            "log": True,
        },
        "scenario": DEFAULT_CONFIG["scenario"],  # not migrated
        "verifier": DEFAULT_CONFIG["verifier"],  # not migrated
    }

    # Schema validate the expected structure
    validate(cast("ConfigData", expected_final_config))

    # Build expected log messages list
    expected_log_messages = []
    molecule_file = tmp_path / "molecule" / "default" / "molecule.yml"
    expected_log_messages.append(
        f"provisioner.playbooks found in {molecule_file}, this can be defined in ansible.playbooks",
    )

    # Clear caplog and create config object
    caplog.clear()
    with caplog.at_level("DEBUG"):
        config_obj = create_config_object(before_config, tmp_path)

    # Compare migrated config to expected for equality
    assert config_obj.config == expected_final_config

    # Confirm DEBUG log statements exist for each migrated key
    for expected_log_message in expected_log_messages:
        assert any(expected_log_message in msg for msg in caplog.messages)


def test_multiple_keys_migration(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Test migration of multiple legacy keys from provisioner to ansible sections.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
        caplog: pytest LogCaptureFixture for capturing log messages.
    """
    # BEFORE: Config with all legacy keys and non-migrated keys in provisioner
    before_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "provisioner": {
            "name": "ansible",
            "ansible_args": ["--verbose"],
            "config_options": {"defaults": {"gathering": "smart"}},
            "env": {"ANSIBLE_FORCE_COLOR": "1"},
            "playbooks": {"converge": "my_converge.yml"},
            # Non-migrated keys should remain
            "options": {"become": True},
            "connection_options": {"ssh_args": "-o ControlMaster=auto"},
            "inventory": {
                "host_vars": {"host1": {"var1": "value1"}},
                "group_vars": {"group1": {"var2": "value2"}},
            },
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validate the before config
    validate(cast("ConfigData", before_config))

    # EXPECTED: Complete expected data structure after all migrations
    expected_final_config = {
        "ansible": {
            "cfg": {
                "defaults": {"gathering": "smart"},  # migrated from provisioner.config_options
            },
            "env": {
                "ANSIBLE_FORCE_COLOR": "1",  # migrated from provisioner.env
            },
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": ["--verbose"],  # migrated from provisioner.ansible_args
                },
            },
            "playbooks": {
                "cleanup": "cleanup.yml",  # default preserved
                "create": "create.yml",  # default preserved
                "converge": "my_converge.yml",  # user override from provisioner.playbooks
                "destroy": "destroy.yml",  # default preserved
                "prepare": "prepare.yml",  # default preserved
                "side_effect": "side_effect.yml",  # default preserved
                "verify": "verify.yml",  # default preserved
            },
        },
        "dependency": DEFAULT_CONFIG["dependency"],  # not migrated
        "driver": DEFAULT_CONFIG["driver"],  # not migrated
        "platforms": [{"name": "instance"}],  # from user config
        "prerun": DEFAULT_CONFIG["prerun"],  # not migrated
        "role_name_check": DEFAULT_CONFIG["role_name_check"],  # not migrated
        "shared_state": DEFAULT_CONFIG["shared_state"],  # not migrated
        "provisioner": {
            "name": "ansible",
            # ansible_args, config_options, env, playbooks removed - migrated to ansible section
            "connection_options": {
                "ssh_args": "-o ControlMaster=auto",
            },  # non-migrated provisioner key
            "options": {"become": True},  # non-migrated provisioner key
            "inventory": {
                "hosts": {},
                "host_vars": {"host1": {"var1": "value1"}},  # non-migrated provisioner key
                "group_vars": {"group1": {"var2": "value2"}},  # non-migrated provisioner key
                "links": {},
            },
            "children": {},
            "log": True,
        },
        "scenario": DEFAULT_CONFIG["scenario"],  # not migrated
        "verifier": DEFAULT_CONFIG["verifier"],  # not migrated
    }

    # Schema validate the expected structure
    validate(cast("ConfigData", expected_final_config))

    # Build expected log messages list
    expected_log_messages = []
    molecule_file = tmp_path / "molecule" / "default" / "molecule.yml"
    expected_log_messages.append(
        f"provisioner.ansible_args found in {molecule_file}, this can be defined in ansible.executor.args.ansible_playbook",
    )
    expected_log_messages.append(
        f"provisioner.config_options found in {molecule_file}, this can be defined in ansible.cfg",
    )
    expected_log_messages.append(
        f"provisioner.env found in {molecule_file}, this can be defined in ansible.env",
    )
    expected_log_messages.append(
        f"provisioner.playbooks found in {molecule_file}, this can be defined in ansible.playbooks",
    )

    # Clear caplog and create config object
    caplog.clear()
    with caplog.at_level("DEBUG"):
        config_obj = create_config_object(before_config, tmp_path)

    # Compare migrated config to expected for equality
    assert config_obj.config == expected_final_config

    # Confirm DEBUG log statements exist for each migrated key
    for expected_log_message in expected_log_messages:
        assert any(expected_log_message in msg for msg in caplog.messages)

    # Test Config properties work correctly
    assert config_obj.provisioner is not None
    assert config_obj.provisioner.ansible_args == ["--verbose"]
    assert config_obj.provisioner.config_options["defaults"]["gathering"] == "smart"
    assert config_obj.provisioner.env["ANSIBLE_FORCE_COLOR"] == "1"


def test_negative_conflicting_ansible_args(tmp_path: Path) -> None:
    """Test that schema rejects config with both ansible.executor.args.ansible_playbook and provisioner.ansible_args.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
    """
    # BEFORE: Config with conflicting ansible_args keys (should fail schema validation)
    conflicting_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "ansible": {
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": ["--new-style"],
                },
            },
        },
        "provisioner": {
            "name": "ansible",
            "ansible_args": [
                "--old-style",
            ],  # This should conflict with ansible.executor.args.ansible_playbook
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validation should fail due to mutual exclusion rule
    validation_errors = validate(cast("ConfigData", conflicting_config))
    assert len(validation_errors) > 0, (
        "Expected validation errors but got none. Schema should reject conflicting keys."
    )

    # Assert the error is specifically about ansible.executor.args vs provisioner.ansible_args conflict
    error_message = validation_errors[0]
    assert "should not be valid under" in error_message, (
        f"Expected mutual exclusion error, got: {error_message}"
    )
    assert "'ansible_args': True" in error_message, (
        f"Expected provisioner.ansible_args conflict, got: {error_message}"
    )
    assert "'args': True" in error_message, (
        f"Expected ansible.executor.args conflict, got: {error_message}"
    )
    assert "'executor'" in error_message, (
        f"Expected ansible.executor conflict, got: {error_message}"
    )


def test_negative_conflicting_config_options(tmp_path: Path) -> None:
    """Test that schema rejects config with both ansible.cfg and provisioner.config_options.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
    """
    # BEFORE: Config with conflicting config_options keys (should fail schema validation)
    conflicting_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "ansible": {
            "cfg": {
                "defaults": {"host_key_checking": False},
            },
        },
        "provisioner": {
            "name": "ansible",
            "config_options": {
                "defaults": {"gathering": "smart"},
            },  # This should conflict with ansible.cfg
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validation should fail due to mutual exclusion rule
    validation_errors = validate(cast("ConfigData", conflicting_config))
    assert len(validation_errors) > 0, (
        "Expected validation errors but got none. Schema should reject conflicting keys."
    )

    # Assert the error is specifically about ansible.cfg vs provisioner.config_options conflict
    error_message = validation_errors[0]
    assert "should not be valid under" in error_message, (
        f"Expected mutual exclusion error, got: {error_message}"
    )
    assert "'config_options': True" in error_message, (
        f"Expected provisioner.config_options conflict, got: {error_message}"
    )
    assert "'cfg': True" in error_message, f"Expected ansible.cfg conflict, got: {error_message}"


def test_negative_conflicting_env(tmp_path: Path) -> None:
    """Test that schema rejects config with both ansible.env and provisioner.env.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
    """
    # BEFORE: Config with conflicting env keys (should fail schema validation)
    conflicting_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "ansible": {
            "env": {
                "ANSIBLE_VERBOSITY": "3",
            },
        },
        "provisioner": {
            "name": "ansible",
            "env": {"ANSIBLE_HOST_KEY_CHECKING": "False"},  # This should conflict with ansible.env
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validation should fail due to mutual exclusion rule
    validation_errors = validate(cast("ConfigData", conflicting_config))
    assert len(validation_errors) > 0, (
        "Expected validation errors but got none. Schema should reject conflicting keys."
    )

    # Assert the error is specifically about ansible.env vs provisioner.env conflict
    error_message = validation_errors[0]
    assert "should not be valid under" in error_message, (
        f"Expected mutual exclusion error, got: {error_message}"
    )
    # Note: Both sides have 'env': True, so we need to check for both ansible and provisioner contexts
    assert "'env': True" in error_message, f"Expected env conflict, got: {error_message}"
    assert error_message.count("'env': True") == EXPECTED_ENV_OCCURRENCES, (
        f"Expected both ansible.env and provisioner.env in conflict, got: {error_message}"
    )


def test_negative_conflicting_playbooks(tmp_path: Path) -> None:
    """Test that schema rejects config with both ansible.playbooks and provisioner.playbooks.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
    """
    # BEFORE: Config with conflicting playbooks keys (should fail schema validation)
    conflicting_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "ansible": {
            "playbooks": {
                "converge": "new_converge.yml",
            },
        },
        "provisioner": {
            "name": "ansible",
            "playbooks": {
                "converge": "old_converge.yml",
            },  # This should conflict with ansible.playbooks
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validation should fail due to mutual exclusion rule
    validation_errors = validate(cast("ConfigData", conflicting_config))
    assert len(validation_errors) > 0, (
        "Expected validation errors but got none. Schema should reject conflicting keys."
    )

    # Assert the error is specifically about ansible.playbooks vs provisioner.playbooks conflict
    error_message = validation_errors[0]
    assert "should not be valid under" in error_message, (
        f"Expected mutual exclusion error, got: {error_message}"
    )
    # Note: Both sides have 'playbooks': True, so we need to check for both ansible and provisioner contexts
    assert "'playbooks': True" in error_message, (
        f"Expected playbooks conflict, got: {error_message}"
    )
    assert error_message.count("'playbooks': True") == EXPECTED_PLAYBOOKS_OCCURRENCES, (
        f"Expected both ansible.playbooks and provisioner.playbooks in conflict, got: {error_message}"
    )


def test_negative_conflicting_multiple_keys(tmp_path: Path) -> None:
    """Test that schema rejects config with multiple conflicting keys.

    Args:
        tmp_path: pytest tmp_path fixture for temporary directory.
    """
    # BEFORE: Config with multiple conflicting keys
    conflicting_config = {
        "dependency": {"name": "galaxy"},
        "driver": {"name": "default"},
        "platforms": [{"name": "instance"}],
        "ansible": {
            "executor": {
                "backend": "ansible-playbook",
                "args": {
                    "ansible_navigator": [],
                    "ansible_playbook": ["--new-style"],
                },
            },
            "cfg": {
                "defaults": {"host_key_checking": False},
            },
            "env": {
                "ANSIBLE_VERBOSITY": "3",
            },
            "playbooks": {
                "converge": "new_converge.yml",
            },
        },
        "provisioner": {
            "name": "ansible",
            "ansible_args": ["--old-style"],
            "config_options": {"defaults": {"gathering": "smart"}},
            "env": {"ANSIBLE_HOST_KEY_CHECKING": "False"},
            "playbooks": {"converge": "old_converge.yml"},
            "options": {"become": True},
            "connection_options": {"ssh_args": "-o ControlMaster=auto"},
            "inventory": {
                "host_vars": {"host1": {"var1": "value1"}},
                "group_vars": {"group1": {"var2": "value2"}},
            },
        },
        "scenario": {"name": "default"},
        "verifier": {"name": "ansible"},
    }

    # Schema validation should fail due to mutual exclusion rule
    validation_errors = validate(cast("ConfigData", conflicting_config))
    assert len(validation_errors) > 0, (
        "Expected validation errors but got none. Schema should reject conflicting keys."
    )

    # JSON Schema validation stops at the first error, so we'll only get 1 error
    # But the error should mention mutual exclusion and one of the specific conflicts
    error_message = validation_errors[0]
    assert "should not be valid under" in error_message, (
        f"Expected mutual exclusion error, got: {error_message}"
    )

    # The error should be about one of the four specific conflicting pairs
    expected_conflicts = [
        # ansible.executor.args vs provisioner.ansible_args
        ("'args': True", "'ansible_args': True"),
        # ansible.cfg vs provisioner.config_options
        ("'cfg': True", "'config_options': True"),
        # ansible.env vs provisioner.env (both sides have 'env': True)
        ("'env': True", "'env': True"),
        # ansible.playbooks vs provisioner.playbooks (both sides have 'playbooks': True)
        ("'playbooks': True", "'playbooks': True"),
    ]

    # Check that the error contains one of the expected conflict pairs
    found_conflict = False
    for ansible_key, provisioner_key in expected_conflicts:
        if ansible_key in error_message and provisioner_key in error_message:
            found_conflict = True
            break

    assert found_conflict, (
        f"Expected one of the specific conflicts {expected_conflicts} in error, got: {error_message}"
    )
