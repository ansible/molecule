---
name: ade
description: >
  Reference for ansible-dev-environment (ade), a pip-like installer for
  Ansible collections with isolated virtual environments. Use ade to set up
  development environments that install both Python and collection
  dependencies, with proper symlinks for editable collection development.
argument-hint: "[subcommand]"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# ade — Ansible Development Environment Manager

## Usage

```text
/ade                    # Show full subcommand reference
/ade install            # How to set up a dev environment
/ade uninstall          # How to tear down
```

ade (ansible-dev-environment) is a pip-like installer for Ansible collections
that creates isolated virtual environments. It reads `galaxy.yml` to determine
collection metadata and installs both Python and Ansible collection
dependencies.

## Hard Rules

1. **Always use `--venv <path>`** to isolate the environment. Never install into the system Python.
2. **`galaxy.yml` must be present.** ade reads it for collection metadata — the command must be run from a directory containing `galaxy.yml` or the path must point to one.
3. **Use `-e` (editable install) for development.** This symlinks the collection into site-packages so changes are reflected immediately.
4. **Activate the venv after install.** ade creates the environment but does not activate it — run `source <venv>/bin/activate` after install.

## Subcommand Reference

| Command | What it does | Example |
|---------|-------------|---------|
| `ade install -e .[test] --venv .venv` | Editable install with test extras | Set up a collection for development and testing |
| `ade install -e .[dev,test] --venv .venv` | Editable install with multiple extras | Include both dev and test dependencies |
| `ade install -e . --venv .venv` | Editable install without extras | Minimal development setup |
| `ade uninstall <namespace>.<name> --venv .venv` | Remove collection from venv | `ade uninstall ansible.scm --venv .venv` |

## Key Behaviors

| Behavior | Detail |
|----------|--------|
| Uses `uv` when available | Falls back to pip if uv is not installed. Set `SKIP_UV=1` to force pip. |
| Editable installs (`-e`) | Symlinks the collection into site-packages for live development |
| Collection dependencies | Reads `galaxy.yml` `dependencies` and installs from Galaxy |
| Python dependencies | Processes `requirements.txt` and `test-requirements.txt` |
| Requires ansible-core | Must be pre-installed in the target venv or system |

## Common Agent Workflows

### "I need to set up a collection for local development"

```bash
git clone <collection_repo>
cd <collection_repo>
ade install -e .[test] --venv .venv
source .venv/bin/activate
```

### "I need to tear down and rebuild the environment"

```bash
rm -rf .venv
ade install -e .[test] --venv .venv
source .venv/bin/activate
```

### "I cloned a collection repo and want to run tests"

```bash
ade install -e .[test] --venv .venv
source .venv/bin/activate
tox -e py                   # see the /tox skill
```

### "ade is using pip but I want it to use uv"

Ensure `uv` is installed and available on `PATH`. ade will use it
automatically. To force pip instead, set `SKIP_UV=1`:

```bash
SKIP_UV=1 ade install -e .[test] --venv .venv
```

## Installation

```bash
pip3 install ansible-dev-tools       # recommended: includes all devtools
pip3 install ansible-dev-environment  # standalone
```

## Configuration

ade reads `galaxy.yml` at the collection root for metadata, dependencies,
and extras. There is no separate ade configuration file. Ensure `galaxy.yml`
is present and valid before running ade commands.
