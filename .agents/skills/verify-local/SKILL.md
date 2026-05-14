---
name: verify-local
description: >
  Detect the project toolchain and run fast, deterministic checks locally
  before pushing. Runs lint and package checks only — lets CI handle
  full tests. Never push without this skill passing.
argument-hint: "[--with-tests]"
user-invocable: true
type: skill
mandatory: false
triggers:
  - "verify locally"
  - "run local checks"
  - "check before push"
  - "run CI locally"
metadata:
  author: Ansible DevTools Team
  version: 1.1.0
---

# Verify Local

Fast, deterministic gate before pushing. Runs lint + package checks
only — the same fast-feedback checks CI runs first. Full tests are
left to CI because they are slow, flaky, and environment-dependent.

**If this skill reports a failure, do NOT push.**

This skill runs commands that modify local state (install deps, build
artifacts). It does not push, commit, or modify remote state.

---

## Why not run tests locally?

- **Tests are flaky.** A false failure blocks a perfectly good lockfile fix.
- **Tests are slow.** `tox -e py` takes 2-10 min. `task wdio` takes 30 min and needs Xvfb.
- **Local != CI.** CI runs across linux/macos/wsl in containers. Local pass doesn't guarantee CI pass.
- **The orchestrator handles test failures.** Push after lint+pkg pass, CI runs full tests, `diagnose-ci` catches failures.

---

## Input

- **No arguments**: run default checks (lint + pkg/package).
- **`--with-tests`**: also run unit tests. Use when the fix changed
  source code (`.ts` or `.py` files), not just lockfile/config.

---

## Entry Gate

Verify you are on a branch (not detached HEAD) and the working tree is
clean (all changes committed):

```bash
git branch --show-current
git status --short
```

The working tree should reflect what you intend to push. Unstaged
changes are allowed — the checks run against the working tree. But
if you see unexpected results, commit first and re-run.

---

## Step 1 — Detect project toolchain

Check what exists in the repo root:

```text
if Taskfile.yml exists AND package.json exists -> TypeScript project
elif tox.ini exists                            -> Python/tox project
elif pyproject.toml exists (no tox.ini)        -> Python/uv project
else                                           -> Unknown, stop
```

15 of 17 devtools repos are Python/tox. Only `vscode-ansible` is
TypeScript. `ansible/actions` is a special case (mixed).

---

## Step 2 — Install dependencies

Use frozen/locked install to match CI:

**TypeScript:**

If `pnpm-lock.yaml` was modified (e.g., lockfile regen fix), use:
```bash
pnpm install
```

Otherwise:
```bash
pnpm install --frozen-lockfile
```

The frozen check is CI's job. Verify-local's job is "will build/lint/pkg
pass," not "is the lockfile in sync."

**Python/tox:**
```bash
uv sync --no-progress -q
```

**Python/uv:**
```bash
uv sync --no-progress -q
```

If install fails, report it and stop — nothing else will work.

---

## Step 3 — Run checks

Run each check sequentially. For each check, capture the exit code
reliably:

```bash
COMMAND_HERE; exit_code=$?
echo "CHECK_NAME: exit_code=$exit_code"
```

Do NOT pipe the command through other commands when capturing exit codes
— that captures the exit code of the pipe's last segment, not the check.

### Default checks (always run)

**TypeScript projects (~2 min total):**

| # | Check | Command | Time | What it catches |
|---|-------|---------|------|-----------------|
| 1 | build | `task build` | ~30s | TypeScript errors, missing exports, tsup bundling |
| 2 | package | `task package` | ~45s | Knip dead code, npm packaging, vitest list |
| 3 | lint | `npx prek run --all-files` | ~30s | ESLint, biome, ruff, codespell, cspell, yamllint, shellcheck |

`task package` is the critical one — it runs knip which catches most
lockfile-related breakage.

**Python/tox projects (~1 min total):**

| # | Check | Command | Time | What it catches |
|---|-------|---------|------|-----------------|
| 1 | lint | `tox -e lint` | ~30-60s | ruff, mypy, pydoclint, pre-commit hooks |
| 2 | pkg | `tox -e pkg` | ~10-20s | Package builds correctly |

**Python/uv projects (~30s total):**

| # | Check | Command | Time | What it catches |
|---|-------|---------|------|-----------------|
| 1 | lint | `uvx pre-commit run --all-files` | ~30s | All pre-commit hooks |

### With `--with-tests` (only when source files changed)

**TypeScript:** add `task test` (+5-15 min)
**Python/tox:** add `tox -e py` (+2-10 min)
**Python/uv:** add `uv run pytest` (+1-5 min)

### Never run locally

These are CI's job — slow, flaky, or environment-dependent:

| Check | Why skip |
|---|---|
| `task e2e` / `task wdio` | Needs VS Code binary, Xvfb, 30+ min |
| `tox -e integration` / `tox -e eco` | Needs external services |
| `tox -e docs` | Only relevant if docs changed |
| `tox -e milestone` | Ecosystem integration tests |

---

## Step 4 — Check if tests are warranted

If `--with-tests` was NOT passed, check what files the current branch
changed compared to the base:

```bash
git diff origin/main --name-only
```

If the diff contains ONLY these file types, tests are NOT needed:

- `pnpm-lock.yaml`, `uv.lock`, `yarn.lock`
- `*.json` (package.json, tsconfig.json, knip config)
- `*.toml` (pyproject.toml)
- `*.yaml` / `*.yml` (CI config, renovate config)

If the diff contains `.ts`, `.py`, `.js`, or `.vue` source files, note
it in the output: "Source files changed — consider `--with-tests`." But
still do NOT run tests by default.

---

## Step 5 — Validate commit message

If there are commits on this branch that are not on the base branch,
validate the latest commit message follows conventional commits:

```bash
msg=$(git log -1 --format="%s")
echo "$msg" | grep -qE "^(fix|feat|chore|docs|style|refactor|test|build|ci)(\(.+\))?: .+" \
  && echo "COMMIT_MSG: valid" || echo "COMMIT_MSG: invalid — must follow conventional commits"
```

---

## Step 6 — Output

```text
## Local Verification

**Toolchain:** TypeScript / Python-tox / Python-uv
**Branch:** branch-name
**Verdict:** ALL PASSING / FAILED
**Duration:** ~Ns total

### Check results
| # | Check   | Status | Duration |
|---|---------|--------|----------|
| 1 | build   | pass   | 12s      |
| 2 | package | pass   | 45s      |
| 3 | lint    | pass   | 30s      |

### Failure details (if any)
**Check:** lint
**Exit code:** 1
**Error:** <last 10 lines of output from the failing check>

### Commit message
**Message:** fix(deps): resolve CI failure from knip update
**Valid:** yes / no

### Source file advisory
Source files changed: yes / no
Tests run: no (default mode)
Advisory: <"Source files changed — consider --with-tests" or "Lockfile/config only — tests not needed">
```

If all checks pass and commit message is valid: **safe to push**.

If any check fails: **do NOT push**. Fix the issue and run `verify-local`
again.
