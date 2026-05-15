---
name: diagnose-ci
description: >
  Fetch CI failure logs for a PR, detect the project toolchain, and
  diagnose the root cause. Outputs a structured diagnosis with the
  failure category, affected files, and suggested fix strategy.
  Use when a PR has failing CI and you need to understand why.
argument-hint: "<repo> <PR number>"
user-invocable: true
type: skill
mandatory: false
triggers:
  - "diagnose CI"
  - "diagnose CI failure"
  - "why is CI failing"
  - "check CI logs"
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# Diagnose CI

Fetch failure logs for a PR, detect the project toolchain, match the
error against known patterns, and output a structured diagnosis.

This skill reads logs and reports findings. It may post a comment on PRs
that need human review — that is its only write action.

---

## Input

Required:

- **repo** — e.g., `ansible/vscode-ansible`
- **PR number** — e.g., `2672`

Optional (from `rebase-pr` output):

- **failing check names** — if provided, skip discovery and fetch logs
  for these checks directly.

---

## Entry Gate

```bash
gh auth status
```

If not authenticated, stop.

---

## Step 1 — Get failing checks

If failing check names were provided as input, use those directly.

Otherwise, fetch them:

```bash
gh pr checks PR_NUMBER --repo OWNER/REPO --json name,state,link \
  --jq '.[] | select(.state == "FAILURE" or .state == "ERROR") | {name, link}'
```

Apply the skip list — ignore these (not code failures):

- `codecov/project`, `codecov/patch`
- `docs/readthedocs.org:*`
- `ack / ack`
- `renovate/stability-days`, `renovate/artifacts`
- `SonarCloud Code Analysis`

If no code failures remain, report that and stop.

---

## Step 2 — Fetch failure logs

Extract the run ID from the check link URL (the numeric segment in
`.../actions/runs/RUN_ID/...`).

Get the failed jobs, their IDs, and failed step names:

```bash
gh api repos/OWNER/REPO/actions/runs/RUN_ID/jobs \
  --jq '.jobs[] | select(.conclusion == "failure") | {id, name, steps: [.steps[] | select(.conclusion == "failure") | .name]}'
```

Save each job's `id` — you need it for per-job log fetching below.

Fetch the logs. The real error is often in the middle of the output, not
the end (the tail is usually cleanup and artifact uploads). Fetch both
ends:

```bash
gh run view RUN_ID --repo OWNER/REPO --log-failed 2>&1 | head -300
gh run view RUN_ID --repo OWNER/REPO --log-failed 2>&1 | tail -300
```

If the output is too noisy, filter per-job using the `JOB_ID` from above:

```bash
gh api repos/OWNER/REPO/actions/jobs/JOB_ID/logs 2>&1 \
  | grep -iE "error|fail|ENOENT|ERR_|assert|exception|fatal" \
  | grep -vE "FORCE_COLOR|if-no-files-found|GITHUB_TOKEN" \
  | head -40
```

---

## Step 3 — Detect project toolchain

Check what exists in the repo root:

```text
if Taskfile.yml exists AND package.json exists -> TypeScript project
   lint command:  task lint / npx prek run --all-files
   build command: task build
   test command:  task test
   package command: task package (runs knip, builds artifacts)
   lock regen:    pnpm install --no-frozen-lockfile

elif tox.ini exists -> Python/tox project
   lint command:  tox -e lint
   test command:  tox -e unit
   lock regen:    uv lock

elif pyproject.toml exists (no tox.ini) -> Python/uv project
   lint command:  uvx pre-commit run --all-files
   test command:  uv run pytest
   lock regen:    uv lock

else -> Unknown toolchain, note in diagnosis
```

This detection can be done via the GitHub API without cloning:

```bash
gh api repos/OWNER/REPO/contents --jq '.[].name' \
  | grep -E "^(Taskfile\.yml|package\.json|tox\.ini|pyproject\.toml)$"
```

---

## Step 4 — Match failure pattern

Read the error output from Step 2. Match against the tables below,
ordered by frequency within each toolchain.

### Node/TypeScript failures

| # | Category | Detection string in logs | Suggested fix |
|---|----------|--------------------------|---------------|
| 1 | **Lockfile out of sync** | `ERR_PNPM_OUTDATED_LOCKFILE`, `frozen-lockfile` | `pnpm install --no-frozen-lockfile`, commit `pnpm-lock.yaml` |
| 2 | **TypeScript build error** | `error TS\d+:` | Read the referenced file:line, fix the type error |
| 3 | **ESLint violations** | `@typescript-eslint/`, `eslint` rule errors | Fix the code at the reported location |
| 4 | **Knip dead code** | `Failed to run task "knip"`, `Extension in project not registered` | Update `knip.ts` config — remove unregistered extensions, suppress pre-existing unused types |
| 5 | **Build artifact missing** | `ENOENT` referencing `dist/` or `.bin/` | Run build first, workspace dep may need rebuild |
| 6 | **Test failure** | `AssertionError`, `expect(` failure | Read the failing test, update to match new dep API |
| 7 | **prek/formatter** | `Files were modified by following hooks`, `prek exited with code 1` | Run `npx prek run --all-files` locally, commit the formatted files |
| 8 | **Biome formatting** | `biome check` diff output | Run `npx biome check --write --unsafe`, commit changes |

### Python/tox failures

| # | Category | Detection string in logs | Suggested fix |
|---|----------|--------------------------|---------------|
| 1 | **Dependency resolution** | `ResolutionFailure`, `Could not find a version`, `conflicting` | Update version constraints in `pyproject.toml` |
| 2 | **Import error** | `ImportError`, `ModuleNotFoundError`, `cannot import name` | Updated dep renamed/moved a module — update import path |
| 3 | **Type check failure** | `mypy` errors with `[code]` suffixes | Fix type annotations |
| 4 | **Lint violation** | `ruff` errors with rule codes (`F401`, `E501`) | Fix the code |
| 5 | **Test failure** | `FAILED tests/`, `AssertionError` | Read the failing test, update assertions |
| 6 | **Lock file conflict** | `uv.lock` mismatch, `pip` resolution error | Regenerate: `uv lock` |
| 7 | **pre-commit failure** | `pre-commit.ci - pr` failing | Run `pre-commit run --all-files`, commit fixes |

### Cross-ecosystem failures

| # | Category | Detection string in logs | Suggested fix |
|---|----------|--------------------------|---------------|
| 1 | **GitHub Actions version** | `Node.js 16 actions are deprecated` | Update action version SHA in workflow YAML |
| 2 | **Merge conflict** | `merge conflict` in PR status | Should have been caught by `rebase-pr` |
| 3 | **Infra/flaky** | Transient network errors, runner timeouts | Re-trigger: `gh run rerun RUN_ID --repo OWNER/REPO --failed` |

---

## Step 5 — Check if failure is pre-existing

Before blaming the dependency update, check if the same failure exists
on the base branch:

Check the last 3 push-triggered runs (scheduled/cron runs may behave
differently):

```bash
gh run list --repo OWNER/REPO --branch BASE_BRANCH --event push --limit 3 \
  --json conclusion --jq '.[].conclusion'
```

If the base branch is consistently failing, this is a **pre-existing
failure**, not caused by the dependency update. Note this in the
diagnosis.

---

## Step 6 — Get the PR diff

```bash
gh pr diff PR_NUMBER --repo OWNER/REPO
```

Understand what the bot changed. This constrains what files should be
touched by a fix — per Shatakshi's guidance: avoid modifying anything
beyond the files already touched by the bot unless absolutely necessary.

Note in the diagnosis which files the bot changed.

---

## Step 7 — Assess fix complexity

Analyze the PR diff, failure diagnosis, and PR metadata to determine if
this is safe to auto-fix.

### 7a. Gather signals

**Version bumps:** Parse the diff for version changes in `package.json`,
`pyproject.toml`, `setup.cfg`, or `requirements*.txt`. A major version
bump is:

- npm: first non-zero number changed (e.g., `^5.9.3` → `^6.0.0`)
- Python: first number changed (e.g., `>=2.1` → `>=3.0`)

**PR metadata:** Check for review comments and blocking labels:

```bash
gh pr view PR_NUMBER --repo OWNER/REPO \
  --json comments,reviews,labels \
  --jq '{
    human_comments: [.comments[] | select((.author.login | endswith("[bot]")) | not)] | length,
    reviews: .reviews | length,
    labels: [.labels[].name]
  }'
```

### 7b. Classify the PR

**AUTO-FIXABLE** — ALL of these must be true:

- Zero major version bumps (or exactly one with a lockfile/config-only fix)
- Failure matches a known pattern from Step 4
- Fix touches 3 or fewer files
- Fix does NOT change: test assertions, CI/workflow config, or source logic
- Fix stays within lockfile, config files, or formatting-only changes
- Not pre-existing on main (Step 5)
- No existing human review comments or reviews on the PR
- No blocking labels (`do-not-merge`, `needs-discussion`, `breaking`, `wontfix`, `on-hold`)
- The fix is one of these safe categories ONLY: lockfile regeneration, formatter/linter auto-fix, removing unused imports, or adding a type annotation on a single line

**NEEDS HUMAN REVIEW** — ANY of these:

1. Multiple major version bumps in one PR
2. Any major version bump that requires source code changes (not just
   lockfile/config)
3. Failure doesn't match any known pattern
4. Pre-existing failure on the base branch
5. Fix would touch more than 3 files
6. Fix requires changing test assertions or expected values
7. Fix requires changing CI/workflow/build config files (`.github/workflows/`,
   `Taskfile.yml`, `tox.ini`, `.pre-commit-config.yaml`)
8. Fix requires changing source logic (not just types/formatting)
9. PR has existing review comments from humans
10. PR has blocking labels (`do-not-merge`, `needs-discussion`, `breaking`,
    `wontfix`, `on-hold`)

The auto-fix path is intentionally narrow. Better to flag 10 PRs for
human review than to silently break one.

### 7c. If NEEDS HUMAN REVIEW — leave a PR comment

First check if a comment already exists (prevent duplicate comments on
repeated runs):

```bash
gh pr view PR_NUMBER --repo OWNER/REPO --json comments \
  --jq '.comments[].body' | grep -q "skill-guardian: diagnose-ci" && echo "ALREADY_COMMENTED" || echo "NO_COMMENT"
```

If no existing comment, post one:

```bash
gh pr comment PR_NUMBER --repo OWNER/REPO --body "$(cat <<'EOF'
## skill-guardian: diagnose-ci

This PR was analyzed automatically and **cannot be auto-fixed**.

**Reason:** <reason from 7b — list all triggered conditions by number>

**Diagnosis summary:**

- <failure 1 category>: <one-line description>
- <failure 2 category>: <one-line description>

**Major version bumps:** <list if any, e.g., typescript 5→6, wdio 8→9>

**Suggested action:** A maintainer should review this PR. <specific
guidance based on the reason — e.g., "Consider splitting the major
version bumps into separate PRs" or "The base branch is failing
independently — fix main first">

_Automated by [skill-guardian](https://github.com/ansible/team-devtools) · diagnose-ci_
EOF
)"
```

---

## Step 8 — Output

```text
## CI Diagnosis

**Repo:** OWNER/REPO
**PR:** #NUMBER — TITLE
**Toolchain:** TypeScript / Python-tox / Python-uv / Unknown
**Pre-existing:** yes / no

### Failure 1: check_name (failed step: step_name)
**Category:** <category from pattern table>
**Error:** <key error line from logs>
**File(s):** <file:line if identifiable>
**Suggested fix:** <specific fix from pattern table>

### Failure 2: check_name (failed step: step_name)
**Category:** <category from pattern table>
**Error:** <key error line from logs>
**File(s):** <file:line if identifiable>
**Suggested fix:** <specific fix from pattern table>

### Bot changed files

- pnpm-lock.yaml
- ...

### Fix scope
<which files need to change — should stay within bot's diff if possible>

### Assessment
**Verdict:** AUTO-FIXABLE / NEEDS HUMAN REVIEW
**Triggered rules:** <list by number, e.g., "#1 multiple major bumps, #2 source code changes required">
**Major bumps:** <list, e.g., "typescript 5→6, @wdio/cli 8→9">
**Files fix would touch:** <count>
**Human reviews on PR:** <count>
**Blocking labels:** <list or "none">
**PR comment posted:** yes / no / already exists
```

Each failed check gets its own numbered section with its own category,
error, and suggested fix. A PR may have multiple independent failures
(e.g., lint fails for one reason, tests fail for a different reason).

If no pattern matches:

```text
### Root cause
**Category:** unknown
**Error:** <raw error lines>

### Suggested fix
Manual investigation needed. Error does not match known patterns.
```
