# Agent Skills

Agent skills for development and maintenance workflow automation in Ansible Devtools.

## Available Skills

### Pull Requests (`pr-*`)

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `pr-new` | Prepare and submit a pull request | `[branch-name] [--title 'PR title']` |
| `pr-review` | Handle PR review feedback | `<PR number>` |
| `pr-contributor-review` | Review and prepare a contributor's PR (upstream/fork) | `<PR number or URL>` |

### Bot PR Maintenance (`fix-bot-prs`, `scan-bot-prs`, `rebase-pr`, `diagnose-ci`, `verify-local`)

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `fix-bot-prs` | Orchestrator: find, diagnose, and fix broken renovate/dependabot PRs | `[repo] [PR number] [--interactive]` |
| `scan-bot-prs` | Scan repos for failing bot PRs, produce prioritized list | `[repo]` |
| `rebase-pr` | Rebase a PR onto main, push, wait for CI | `<repo> <PR number>` |
| `diagnose-ci` | Fetch CI failure logs, categorize, assess fix complexity | `<repo> <PR number>` |
| `verify-local` | Run lint + pkg checks locally before pushing | `[--with-tests]` |

### Utilities

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `tox` | tox environment reference (lint, test, docs, pkg) | `[environment-name]` |

## Skill Structure

```text
skills/
├── README.md                   ← You are here
├── diagnose-ci/
│   └── SKILL.md
├── fix-bot-prs/
│   └── SKILL.md
├── pr-contributor-review/
│   └── SKILL.md
├── pr-new/
│   └── SKILL.md
├── pr-review/
│   └── SKILL.md
├── rebase-pr/
│   └── SKILL.md
├── scan-bot-prs/
│   └── SKILL.md
├── tox/
│   └── SKILL.md
└── verify-local/
    └── SKILL.md
```

## SKILL.md Format

Each skill has YAML front matter:

```yaml
---
name: skill-name
description: >-
  What the skill does. When to use it. Trigger phrases.
argument-hint: "[expected arguments]"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---
```

## Version

- **Version**: 1.0.0
- **Author**: Ansible DevTools Team
- **License**: GPL-3.0-or-later
