---
name: pr-new
description: >
  Prepare and submit a pull request. Syncs with upstream,
  creates a feature branch, runs quality gates (tox -e lint, tox -e py),
  updates documentation as needed, commits with conventional commits,
  then creates the PR via gh. Use when the user asks to submit, create, or open
  a pull request, or says "submit PR", "open PR", "create PR", "new PR".
argument-hint: "[branch-name] [--title 'PR title']"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# PR New

## Workflow

### Step 1: Sync with upstream and create a feature branch

Always start from the latest upstream main:

```bash
git fetch upstream
git checkout -b <branch-name> upstream/main
```

Use a descriptive branch name (e.g., `feat/add-jira-labels`, `fix/check-constraints`).

If changes already exist on the current branch (e.g., from an in-progress session), cherry-pick or rebase them onto the new branch.

### Step 2: Run quality gates

```bash
tox -e lint
tox -e py
```

**Both must pass cleanly on the full tree** — not just the files you changed.
If the branch has pre-existing violations (e.g., from an old base), rebase onto `upstream/main` first.

Do **not** run `ruff`, `mypy`, `prek`, or `pytest` directly — always use tox.
See the `/tox` skill for the full environment reference.

### Step 3: Update documentation

Check whether your changes affect areas covered by existing docs. Update any that apply:

| Doc | When to update |
|-----|----------------|
| `README.md` | Project overview, setup changes, dependency updates |
| `docs/` | Guides, references, or user-facing documentation |
| `CONTRIBUTING.md` | Contribution workflow or policy changes |
| `AGENTS.md` | Agent behavior, skill references, static check config |

### Step 4: Commit with conventional commits

Use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types for this project:

| Type | When to use |
|------|-------------|
| `feat` | New feature (CLI command, workflow, utility) |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style/formatting (no logic change) |
| `refactor` | Code restructuring (no feature or fix) |
| `test` | Adding or updating tests |
| `build` | Build system, dependencies |
| `ci` | CI/CD configuration |
| `chore` | Maintenance tasks |

Scopes reflect project areas: `jira`, `check`, `docs`, `ci`, `deps`, `config`.

Examples:

- `feat(jira): add bulk issue creation support`
- `fix(check): handle missing platform constraints gracefully`
- `docs: update release process guide`
- `ci: add Python 3.14 to test matrix`

Include ticket references in the commit footer:

- `Fixes: #123` for GitHub issues
- `Related: AAP-123` for JIRA tickets
- Do not use URLs — use plain text references

### Step 5: Push and create the pull request

```bash
git push -u origin HEAD

gh pr create --repo <upstream-owner>/<repo> --title "conventional commit style title" --body "$(cat <<'EOF'
## Summary
- Concise description of what changed and why

## Changes
- List of notable changes

## Quality of life
- List any non-functional improvements bundled in this PR: skill updates,
  workflow fixes, documentation for contributor experience, etc.
- Omit this section entirely if there are none.

## Test plan
- [ ] `tox -e lint` passes
- [ ] `tox -e py` passes
- [ ] Docs updated (if applicable)
EOF
)"
```

The PR targets upstream's `main` branch from the fork. Return the PR URL to the user.

### Including non-code changes (Quality of life)

PRs often include changes that are not directly part of the feature or fix but
improve the development workflow: skill updates, CI/CD tweaks, pre-commit
config changes, documentation for contributor experience, or process fixes.

These changes belong in the **Quality of life** section of the PR body. Use
this section whenever the PR touches files like `.agents/skills/`, `AGENTS.md`,
`CLAUDE.md`, `.github/workflows/`, `.pre-commit-config.yaml`, `CONTRIBUTING.md`,
or similar workflow artifacts. This makes it easy for reviewers to separate
functional changes from process improvements.

If a PR contains **only** quality-of-life changes (no production code), use
`chore` or `docs` as the commit type.

### Maintaining the PR

When pushing additional commits to an existing PR, **always update the PR body** to reflect the new changes:

```bash
gh pr edit <pr-number> --body "$(cat <<'EOF'
...updated body...
EOF
)"
```

The Summary, Changes, and Test plan sections must stay current with all commits on the branch, not just the initial one.

### Responding to review feedback

After pushing the PR, reviewers (human or Copilot) may leave comments. Follow
the **`pr-review`** skill for the full procedure: checking CI status, replying
to comments, resolving threads, and re-checking for new Copilot reviews.
