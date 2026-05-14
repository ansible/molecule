---
name: fix-bot-prs
description: >
  Orchestrator that finds broken renovate/dependabot PRs across Ansible
  devtools repos, diagnoses failures, applies safe fixes, verifies
  locally, pushes, and monitors CI. Composes scan-bot-prs, rebase-pr,
  diagnose-ci, and verify-local into a single automated workflow.
argument-hint: "[repo] [PR number] [--interactive]"
user-invocable: true
type: workflow
mandatory: false
requires:
  - scan-bot-prs
  - rebase-pr
  - diagnose-ci
  - verify-local
triggers:
  - "fix bot PRs"
  - "fix renovate PRs"
  - "fix dependabot PRs"
  - "fix dependency PRs"
  - "fix broken dependency updates"
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# Fix Bot PRs

Orchestrator workflow that composes four skills to find, diagnose, and
fix broken dependency update PRs across Ansible devtools repositories.

**Default mode is fully automatic.** Pass `--interactive` to choose PRs
manually.

---

## Skills used

| Skill | Purpose | Write actions |
|-------|---------|---------------|
| `scan-bot-prs` | Find failing bot PRs, prioritize | None (read-only) |
| `rebase-pr` | Rebase onto main, push, wait for CI | git push |
| `diagnose-ci` | Fetch logs, categorize failure, assess risk | May comment on PR |
| `verify-local` | Run lint+pkg locally before pushing | Local only |

---

## Input

- **No arguments**: scan all repos, auto-pick highest priority, fix it.
- **repo** (e.g., `ansible/vscode-ansible`): scan only that repo.
- **repo + PR number**: skip scanning, fix that specific PR.
- **`--interactive`**: show the prioritized list, let user choose.

---

## The workflow

```text
┌─────────────────┐
│  scan-bot-prs   │ → prioritized list of failing PRs
└────────┬────────┘
         │ pick top priority (or user chooses)
         ▼
┌─────────────────┐
│   rebase-pr     │ → rebase onto main, push, wait for CI
└────────┬────────┘
         │ CI still failing?
         ▼
┌─────────────────┐
│  diagnose-ci    │ → categorize failure, assess fix complexity
└────────┬────────┘
         │ AUTO-FIXABLE?
         ▼
    ┌────┴────┐
    │  YES    │  NEEDS HUMAN REVIEW → comment on PR, skip, next PR
    └────┬────┘
         │ apply fix
         ▼
┌─────────────────┐
│  verify-local   │ → lint + pkg pass locally?
└────────┬────────┘
         │ pass? → commit, push, wait for CI
         │ fail? → iterate on fix (max 3 attempts)
         ▼
    ┌────┴────┐
    │ CI pass │  CI fail → loop back to diagnose-ci (max 3 attempts)
    └────┬────┘
         │
         ▼
      report + next PR
```

---

## Step 1 — Discover

Run `scan-bot-prs` (or skip if a specific PR was provided).

If `--interactive`, display the prioritized table and let the user pick.
Otherwise, auto-pick the top priority PR.

If no failing PRs found, report and stop.

---

## Step 2 — Rebase

Run `rebase-pr` with the selected repo and PR number.

**If rebase result says "CI all passing":** PR is fixed. Report success,
move to next PR in the queue.

**If rebase result says "N code failures":** proceed to Step 3.

**If rebase result says "push rejected" or "conflicts (aborted)":**
skip this PR, report why, move to next PR.

---

## Step 3 — Diagnose

Run `diagnose-ci` with the repo and PR number. Pass the failing check
names from the rebase-pr output so it skips rediscovery.

**If assessment is NEEDS HUMAN REVIEW:** `diagnose-ci` already posted
a comment on the PR. Skip this PR, report why, move to next PR.

**If assessment is AUTO-FIXABLE:** proceed to Step 4.

---

## Step 4 — Fix

### STOP CHECK — read this before doing anything

Re-read the `diagnose-ci` output. Check the **Verdict** field.

**If Verdict is `NEEDS HUMAN REVIEW`:** STOP. Do NOT proceed. Do NOT
apply any fix. Do NOT modify any file. Do NOT commit. Do NOT push.
Skip this PR immediately and move to the next one. This is not a
suggestion — it is a hard rule. The comment has already been posted
on the PR by `diagnose-ci`. There is nothing left to do.

**If Verdict is `AUTO-FIXABLE`:** proceed below.

### 4a. Scope the fix

- Prefer fixing within the files the bot already changed (lockfile, package.json, pyproject.toml).
- If the fix requires touching other files (e.g., knip config, tsconfig), keep it minimal.
- Never change test assertions, CI workflow files, or source logic.

### 4b. Apply by category

**Lockfile regeneration:**
```bash
pnpm install          # TypeScript
uv lock               # Python
```
Commit the regenerated lockfile.

**Formatter/linter auto-fix:**
```bash
npx prek run --all-files    # TypeScript
tox -e lint                 # Python (some linters auto-fix)
```
Commit any auto-formatted files.

**Removing unused imports:**
Read the error output, remove the specific imports listed.

**Adding a type annotation on a single line:**
Read the error output, add the minimal type fix.

### 4c. Commit

Use conventional commits:

```bash
git add <specific-files-only>
git commit -m "fix(deps): <what was fixed>

<one-line description of what broke and why>"
```

Never `git add -A` or `git add .`.

---

## Step 5 — Verify locally

Run `verify-local`. This is a **hard gate** — if it fails, do NOT push.

**If verify-local passes:** proceed to Step 6.

**If verify-local fails:** read the failure output, fix the issue, and
run verify-local again. Max 3 local fix iterations. If still failing
after 3 attempts, skip this PR and report.

---

## Step 6 — Push and monitor CI

```bash
git push
```

Then poll CI until all jobs complete (same polling logic as `rebase-pr`):

```bash
elapsed=0
while true; do
  checks=$(gh pr checks PR_NUMBER --repo OWNER/REPO \
    --json name,state --jq '.[] | select(.state != "SKIPPED")')
  total=$(echo "$checks" | grep -c . || true)
  pending=$(echo "$checks" | grep -cE "IN_PROGRESS|PENDING|QUEUED" || true)

  if [ "$total" -eq 0 ] && [ "$elapsed" -ge 300 ]; then
    echo "TIMEOUT: no checks appeared after 5 minutes"
    break
  fi

  if [ "$total" -gt 0 ] && [ "$pending" -eq 0 ]; then
    break
  fi

  sleep 60
  elapsed=$((elapsed + 60))
done
```

**If all code checks pass:** report success. Move to next PR.

**If code checks still fail:** this is attempt N of 3. Loop back to
Step 3 with the new failure logs. If at attempt 3, skip and report.

---

## Step 7 — Report

After processing each PR (whether fixed, skipped, or failed), produce
a summary. After all PRs are processed, produce a final report.

### 7a. Verify PR state — MANDATORY

Before reporting on any PR, verify its actual state. Do NOT assume a PR
is merged, closed, or open — check explicitly:

```bash
gh pr view PR_NUMBER --repo OWNER/REPO \
  --json state,mergedAt --jq '{state, mergedAt}'
```

Use the returned `state` (OPEN / MERGED / CLOSED) in the report. Never
infer or guess the state from other signals.

### Per-PR report

```text
## PR #NUMBER — TITLE (REPO)

**PR state:** OPEN / MERGED / CLOSED (verified via gh pr view)
**Result:** Fixed / Skipped (NEEDS HUMAN REVIEW) / Skipped (conflicts) /
            Skipped (push rejected) / Failed (3 attempts exhausted)
**Attempts:** N/3
**Action taken:** rebase only / lockfile regen / config fix / formatter auto-fix

### What was done

- Rebased onto main
- <commit description>

### CI Status

- lint: pass
- preflight: pass
- test (linux): pass
- ...
```

### Final summary

```text
## Fix Bot PRs — Run Summary

**Date:** YYYY-MM-DD HH:MM
**PRs processed:** N
**Fixed:** X
**Skipped (human review):** Y
**Skipped (other):** Z
**Failed:** W

### Fixed PRs

- ansible/vscode-ansible #2716 — lockfile regen
- ansible/molecule #4629 — rebase only

### Skipped PRs

- ansible/vscode-ansible #2672 — NEEDS HUMAN REVIEW (4 major version bumps)
- ansible/ansible-sign #115 — push rejected (fork PR)

### Failed PRs

- ansible/ansible-lint #5011 — 3 attempts exhausted (tox lint failure)
```

---

## Safety rules

1. **Never push without `verify-local` passing.**
2. **Never force-push** except `--force-with-lease` after a rebase.
3. **Never change test assertions** — if tests fail, that's a human call.
4. **Never change CI/workflow config files.**
5. **Never change source logic** — only lockfiles, config, formatting,
   unused imports, single-line type annotations.
6. **Never merge the PR** — only fix CI. Let automerge or a human
   reviewer handle the merge.
7. **Never commit secrets, tokens, or credentials.**
8. **Stage specific files only** — never `git add -A` or `git add .`.
9. **NEEDS HUMAN REVIEW = STOP.** If `diagnose-ci` returns NEEDS HUMAN
   REVIEW, do NOT apply any fix, modify any file, commit, or push.
   The comment is already posted. Skip the PR and move to the next one.
   No exceptions. No "but it's a simple fix." STOP.
10. **Max 3 attempts per PR** — prevents infinite loops.

---

## Processing multiple PRs

When scanning all repos, process PRs in priority order (security first,
then lockfile, then single dep, then all deps). After each PR:

1. If fixed: move to next PR.
2. If skipped or failed: log the reason, move to next PR.
3. Continue until all failing PRs are processed or a reasonable time
   limit is reached.

The orchestrator should process PRs from different repos without
assuming any shared state between them. Each PR is independent.
