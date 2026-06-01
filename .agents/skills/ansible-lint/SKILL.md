---
name: ansible-lint
description: >
  Reference for linting Ansible playbooks, roles, and collections with
  ansible-lint. Agents should prefer tox -e lint when available, but this
  skill provides the canonical reference for ansible-lint options, profiles,
  rule suppression, and configuration when direct invocation is needed or
  when understanding lint output.
argument-hint: "[options]"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# ansible-lint — Ansible Playbook & Role Linter

## Usage

```text
/ansible-lint                  # Show full option reference
/ansible-lint profiles         # Profile progression reference
/ansible-lint suppress         # How to suppress rules
/ansible-lint config           # Configuration file reference
```

ansible-lint checks playbooks, roles, and collections against best-practice
rules. In DevTools repos, prefer `tox -e lint` which runs ansible-lint as
part of the full quality gate. Use this skill to understand lint output,
choose profiles, or configure suppression.

## Hard Rules

1. **In DevTools repos, prefer `tox -e lint`** over running `ansible-lint` directly. See the `/tox` skill.
2. **Always run from the project root.** ansible-lint uses the working directory to locate configuration, roles, and dependencies.
3. **Review `--fix` output before committing.** Never auto-fix and commit blindly.
4. **Never use blanket `# noqa`** without a rule ID. Always use `# noqa: rule-id[subrule]`.
5. **Do not lower the profile to silence violations** — fix the violations or use targeted suppression.

## Profile Reference

Profiles are progressive — each level includes all rules from lower levels.

| Profile | Strictness | Typical use |
|---------|-----------|-------------|
| `min` | Lowest | Critical syntax/parse errors only — legacy code migration |
| `basic` | Low | min + basic best practices — getting started |
| `moderate` | Medium | basic + style and naming — active development |
| `safety` | High | moderate + security patterns — production-bound code |
| `shared` | Higher | safety + community standards — shared/published content |
| `production` | Highest | All rules — production deployments |

## Key Options

| Option | Purpose | Example |
|--------|---------|---------|
| `--profile <name>` | Set strictness level | `ansible-lint --profile production` |
| `--fix [WRITE_LIST]` | Auto-fix violations | `ansible-lint --fix` |
| `-f <format>` | Output format (brief, full, json, sarif, pep8) | `ansible-lint -f json` |
| `-t <tags>` | Include only matching rule tags | `ansible-lint -t yaml` |
| `-x <rules>` | Skip specific rules | `ansible-lint -x yaml[truthy]` |
| `-w <rules>` | Treat as warnings (non-blocking) | `ansible-lint -w name[casing]` |
| `--enable-list` | Activate optional rules | `ansible-lint --enable-list no-log-password` |
| `-s` / `--strict` | Warnings become errors | `ansible-lint --strict` |
| `--offline` | Skip galaxy dep install and schema refresh | `ansible-lint --offline` |
| `--generate-ignore` | Create/update .ansible-lint-ignore | `ansible-lint --generate-ignore` |
| `-c <file>` | Use specific config file | `ansible-lint -c .config/ansible-lint.yml` |
| `--project-dir <dir>` | Set project root directory | `ansible-lint --project-dir ./roles/myrole` |
| `--exclude <path>` | Skip directories or files (repeatable) | `ansible-lint --exclude tests/` |

## Suppression Methods

### Inline suppression

Add `# noqa: rule-id` to the end of the offending line. Multiple rules can be space-separated:

```yaml
- name: Example task  # noqa: command-instead-of-module no-changed-when
  command: echo hello
```

### Ignore file

Create `.ansible-lint-ignore` (or `.config/ansible-lint-ignore.txt`) with one entry per line:

```text
playbooks/legacy.yml yaml[truthy]
roles/old_role/tasks/main.yml name[casing]
```

### Config file skip/warn lists

```yaml
skip_list:
  - yaml[truthy]
warn_list:
  - name[casing]
```

## Configuration Files

| File | Purpose |
|------|---------|
| `.ansible-lint` | Primary config (YAML) |
| `.ansible-lint.yml` / `.ansible-lint.yaml` | Alternative names |
| `.config/ansible-lint.yml` | XDG-style location |
| `.ansible-lint-ignore` | Per-file rule suppression |

Example configuration:

```yaml
profile: moderate
skip_list:
  - yaml[truthy]
warn_list:
  - name[casing]
exclude_paths:
  - .cache/
  - .tox/
offline: false
```

## Common Agent Workflows

### "I need to understand a lint failure"

Read the rule ID from the output (e.g., `yaml[truthy]`). Check the project
profile in `.ansible-lint` or `.ansible-lint.yml`. Decide whether to fix the
violation or add targeted suppression.

### "I want to lint only specific files"

```bash
ansible-lint playbooks/site.yml roles/myrole/
```

### "I need to auto-fix violations"

```bash
ansible-lint --fix
git diff                     # review every change before committing
```

### "I need to suppress a rule for one file"

```bash
echo 'playbooks/legacy.yml yaml[truthy]' >> .ansible-lint-ignore
```

### "I want to check what profile the project uses"

Look for the `profile:` key in `.ansible-lint`, `.ansible-lint.yml`, or
`.config/ansible-lint.yml` at the project root.

## Installation

```bash
pip3 install ansible-dev-tools   # recommended: includes all devtools
pip3 install ansible-lint        # standalone
```

## Configuration

ansible-lint configuration lives in `.ansible-lint`, `.ansible-lint.yml`, or
`.config/ansible-lint.yml` at the project root. The cache directory defaults
to `{project_dir}/.cache/` and should be added to `.gitignore`. Environment
variables like `ANSIBLE_LINT_CUSTOM_RULESDIR` and `ANSIBLE_LINT_IGNORE_FILE`
can override defaults.
