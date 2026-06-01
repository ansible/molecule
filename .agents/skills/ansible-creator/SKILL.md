---
name: ansible-creator
description: >
  Reference for scaffolding Ansible content with ansible-creator.
  Use ansible-creator to initialize new collections, playbook projects,
  and execution environments, or to add plugins and resources to existing
  projects. This skill is the canonical lookup table for which subcommand
  and flags to use.
argument-hint: "[subcommand]"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# ansible-creator — Ansible Content Scaffolding Tool

## Usage

```text
/ansible-creator                  # Show full subcommand reference
/ansible-creator init             # How to scaffold new projects
/ansible-creator add              # How to add plugins/resources
```

ansible-creator scaffolds Ansible content projects. Use `init` to create new
projects from scratch and `add` to extend existing ones with plugins or
resources.

## Hard Rules

1. **Always use `namespace.name` format** for `init collection` and `init playbook`.
2. **Never scaffold into a non-empty directory** without `-o/--overwrite` — the command will fail.
3. **After scaffolding, run `tox -e lint`** to verify the generated content passes quality gates. See the `/tox` skill.
4. **`add plugin` requires the collection root** — the path must point to the directory containing `galaxy.yml`.

## Subcommand Reference

### Initialize projects

| Command | What it creates | Example |
|---------|----------------|---------|
| `ansible-creator init collection <ns>.<name> <path>` | Full collection skeleton (plugins, roles, tests, docs, galaxy.yml) | `ansible-creator init collection myorg.network ~/collections/ansible_collections` |
| `ansible-creator init playbook <ns>.<name> <path>` | Playbook project structure | `ansible-creator init playbook myorg.deploy ~/projects/deploy` |
| `ansible-creator init execution_env <path>` | Execution environment definition files | `ansible-creator init execution_env ~/ee-project` |

### Add to existing projects

#### Resources

| Command | What it adds |
|---------|-------------|
| `ansible-creator add resource devcontainer <path>` | Dev container configuration |
| `ansible-creator add resource devfile <path>` | Devfile for cloud IDEs |
| `ansible-creator add resource execution-environment <path>` | Sample EE YAML template |
| `ansible-creator add resource play-argspec <path>` | Playbook argument specification examples |
| `ansible-creator add resource role <path>` | New role skeleton |

#### Plugins

| Command | What it adds | Example |
|---------|-------------|---------|
| `ansible-creator add plugin action <name> <coll-path>` | Action plugin | `ansible-creator add plugin action my_action .` |
| `ansible-creator add plugin filter <name> <coll-path>` | Filter plugin | `ansible-creator add plugin filter my_filter .` |
| `ansible-creator add plugin lookup <name> <coll-path>` | Lookup plugin | `ansible-creator add plugin lookup my_lookup .` |
| `ansible-creator add plugin module <name> <coll-path>` | Module plugin | `ansible-creator add plugin module my_module .` |
| `ansible-creator add plugin test <name> <coll-path>` | Test plugin | `ansible-creator add plugin test my_test .` |

## Common Flags

| Flag | Purpose |
|------|---------|
| `-o` / `--overwrite` | Overwrite existing files |
| `-no` / `--no-overwrite` | Fail if destination exists (default) |
| `--json` | Output in JSON format |
| `-v` | Increase verbosity (up to `-vvv`) |
| `--log-file <path>` | Write log to file |
| `--na` / `--no-ansi` | Disable colored output |
| `--ll` / `--log-level` | Set logging level (debug, info, warning, error, critical) |

## Common Agent Workflows

### "I need to start a new Ansible collection"

```bash
ansible-creator init collection myorg.mynetwork ~/collections/ansible_collections
cd ~/collections/ansible_collections/myorg/mynetwork
tox -e lint
```

### "I need to add a module plugin to an existing collection"

```bash
cd /path/to/collection       # must contain galaxy.yml
ansible-creator add plugin module my_new_module .
```

### "I need to scaffold an execution environment"

```bash
ansible-creator init execution_env ~/ee-project
```

### "The target directory already has files"

Use `--overwrite` to replace existing files, or choose a clean path:

```bash
ansible-creator init collection myorg.mynetwork ~/collections/ansible_collections --overwrite
```

## Installation

```bash
pip3 install ansible-dev-tools   # recommended: includes all devtools
pip3 install ansible-creator     # standalone
```

## Configuration

ansible-creator does not use a configuration file. All options are passed as
CLI flags. Scaffolded projects may include their own `pyproject.toml`,
`galaxy.yml`, and `tox.ini` for downstream configuration.
