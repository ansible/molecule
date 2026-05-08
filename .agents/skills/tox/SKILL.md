---
name: tox
description: >
  Reference for running lint, test, build, and doc commands via tox.
  Agents MUST use tox for all quality gates — never invoke pytest, ruff,
  mypy, prek, or shell scripts directly. This skill is the canonical
  lookup table for which tox environment to use.
argument-hint: "[environment-name]"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# tox — Sole Developer & Agent Orchestration Tool

## Usage

```text
/tox                  # Show full environment reference
/tox lint             # How to run lint
/tox py               # How to run tests
/tox docs             # How to build docs
/tox <env>            # Lookup any tox environment
```

tox is the **only** way to run lint, test, build, and doc commands in this
project. Do not invoke `pytest`, `ruff`, `mypy`, `prek`, or shell scripts
directly. Every task maps to a `tox -e <env>` command.

## Hard Rules

1. **Never run `pytest` directly.** Use `tox -e py`.
2. **Never run `ruff`, `mypy`, or `prek` directly.** Use `tox -e lint`.
3. **Pass extra arguments after `--`.** Example: `tox -e py -- -k test_example`.
4. **In CI, use `uvx --with tox-uv tox -e <env>`** instead of installing tox.

## Environment Reference

### Quality gates

| Environment | What it runs | When to use |
|-------------|-------------|-------------|
| `tox -e lint` | `prek run --all-files` (ruff, mypy, biome, tombi, codespell, ansible-lint) | Before every commit. Verification step for all tasks. |

### Test suites

| Environment | What it runs | When to use |
|-------------|-------------|-------------|
| `tox -e py` | `pytest` with coverage (threshold varies per repo) | After any code change. |
| `tox -e py -- -k <pattern>` | Single test or test pattern | Debugging a specific test. |
| `tox -e py -- --no-cov` | Tests without coverage overhead | Quick iteration. |
| `tox -e devel` | Tests with newest deps (no lock, prereleases allowed) | Verifying forward compatibility. |

### Documentation

| Environment | What it runs | When to use |
|-------------|-------------|-------------|
| `tox -e docs` | `mkdocs build --strict` | After doc changes. |

### Packaging

| Environment | What it runs | When to use |
|-------------|-------------|-------------|
| `tox -e pkg` | `python -m build` + `twine check --strict` | Before release. Verify package metadata. |

### Dependency management

| Environment | What it runs | When to use |
|-------------|-------------|-------------|
| `tox -e deps` | `prek run deps` + `prek autoupdate` + `tox -e lint` | Bumping all dependencies. |

### Default set

Running `tox` with no `-e` flag executes the default environment list defined
in the repo's `pyproject.toml` or `tox.ini`. This is the full quality gate.

**Note:** Not all environments listed above are available in every repo. Run
`tox l` to discover the environments available in the current repository.

## Common Agent Workflows

### "I changed Python code, what do I run?"

```bash
tox -e lint              # check style + types
tox -e py                # run tests
```

### "I changed documentation"

```bash
tox -e docs              # build and verify docs
```

### "I need to run one specific test"

```bash
tox -e py -- -k test_example
tox -e py -- test/test_example.py::test_specific_function
```

### "I want to verify everything before a PR"

```bash
tox -e lint
tox -e py
```

### "List all available environments"

```bash
tox l
```

## Installation

```bash
uv tool install tox --with tox-uv
```

## Configuration

Tox configuration typically lives in `pyproject.toml` under `[tool.tox]` or in
a standalone `tox.ini`. Environment definitions, extras, pass-through env vars,
and commands are all there. Do not scatter test/lint invocations across
Makefiles, scripts, or workflow YAML.
