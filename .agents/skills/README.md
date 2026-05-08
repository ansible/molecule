# Agent Skills

Agent skills for development and maintenance workflow automation in Ansible Devtools.

## Available Skills

### Pull Requests (`pr-*`)

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `pr-new` | Prepare and submit a pull request | `[branch-name] [--title 'PR title']` |
| `pr-review` | Handle PR review feedback | `<PR number>` |
| `pr-contributor-review` | Review and prepare a contributor's PR (upstream/fork) | `<PR number or URL>` |

### Utilities

| Skill | Purpose | Arguments |
|-------|---------|-----------|
| `tox` | tox environment reference (lint, test, docs, pkg) | `[environment-name]` |

## Skill Structure

```text
skills/
├── README.md                   ← You are here
├── pr-new/
│   └── SKILL.md
├── pr-review/
│   └── SKILL.md
├── pr-contributor-review/
│   └── SKILL.md
└── tox/
    └── SKILL.md
```

## SKILL.md Format

Each skill has YAML frontmatter:

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
