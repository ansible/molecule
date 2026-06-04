---
name: rebase-pr
description: >
  Check out a PR branch, rebase it onto the base branch, push, and wait
  for CI to complete. Reports whether the rebase alone fixed CI or if
  further action is needed. Use when a PR is stale and may just need a
  rebase to pass CI.
argument-hint: "<repo> <PR number>"
user-invocable: true
type: skill
mandatory: false
triggers:
  - "rebase PR"
  - "rebase bot PR"
  - "update PR branch"
  - "sync PR with main"
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# Rebase PR

Check out a PR branch, rebase it onto the base branch (usually `main`),
push, and poll CI until all jobs complete. Report the result.

This skill does **one thing** — rebase and report. It does not diagnose
or fix CI failures.

---

## Input

Required:

- **repo** — e.g., `ansible/vscode-ansible`
- **PR number** — e.g., `2716`

---

## Entry Gate

```bash
gh auth status
```

If not authenticated, stop.

Verify the PR exists and is open:

```bash
gh pr view PR_NUMBER --repo OWNER/REPO \
  --json state,headRefName,baseRefName \
  --jq '{state, head: .headRefName, base: .baseRefName}'
```

If the PR is not open, stop.

---

## Step 1 — Check out the PR branch

If the target repo is your current working directory:

```bash
gh pr checkout PR_NUMBER
```

Otherwise clone first:

```bash
gh repo clone OWNER/REPO /tmp/rebase-pr-REPO
cd /tmp/rebase-pr-REPO
gh pr checkout PR_NUMBER
```

---

## Step 2 — Check if rebase is needed

```bash
git fetch origin BASE_BRANCH
git log --oneline origin/BASE_BRANCH..HEAD | wc -l
git merge-base --is-ancestor origin/BASE_BRANCH HEAD && echo "UP_TO_DATE" || echo "BEHIND"
```

If `UP_TO_DATE`, the branch already includes all commits from the base
branch. No rebase or push is needed — no new CI run will be triggered.
Skip to Step 5 and report the existing CI results. Make it clear in the
output that these are **existing results, not from a new run**.

---

## Step 3 — Rebase

```bash
git rebase origin/BASE_BRANCH
```

**If rebase succeeds cleanly:**

Push the rebased branch:

```bash
git push --force-with-lease
```

If push is rejected, stop and report:

```text
**Action taken:** push rejected (branch was modified remotely)
```

Do not attempt to pull and reconcile — the bot branch moved under you.
The orchestrator can decide to retry or skip.

If the PR head branch is on a fork (different owner than the repo),
`--force-with-lease` will fail because you lack push access to the fork.
Report that fork PRs cannot be rebased by this skill and stop.

**If rebase has conflicts:**

Count the conflicting files:

```bash
git diff --name-only --diff-filter=U
```

If 3 or fewer files conflict, attempt resolution:

- For lock files (`pnpm-lock.yaml`, `uv.lock`, `yarn.lock`): accept theirs and regenerate after rebase.
- For other files: abort and report that manual conflict resolution is needed.

```bash
git checkout --theirs pnpm-lock.yaml  # or uv.lock
git add pnpm-lock.yaml
git rebase --continue
```

If more than 3 files conflict or non-lock-file conflicts exist:

```bash
git rebase --abort
```

Report that the rebase has conflicts requiring manual resolution and stop.

---

## Step 4 — Poll CI until complete

Poll every 60 seconds until no jobs are `IN_PROGRESS` or `PENDING`.

If after 5 minutes **no checks have appeared at all** (CI never started),
report a timeout and stop — workflows may be disabled or misconfigured.

Once at least one check is running or completed, keep polling with no
time limit until all jobs finish. CI duration varies across repos — some
jobs take 5 minutes, others 30+.

```bash
elapsed=0
while true; do
  checks=$(gh pr checks PR_NUMBER --repo OWNER/REPO \
    --json name,state --jq '.[] | select(.state != "SKIPPED")')
  total=$(echo "$checks" | grep -c . || true)
  pending=$(echo "$checks" | grep -cE "IN_PROGRESS|PENDING|QUEUED" || true)

  # CI never started — timeout after 5 minutes
  if [ "$total" -eq 0 ] && [ "$elapsed" -ge 300 ]; then
    echo "TIMEOUT: no checks appeared after 5 minutes"
    break
  fi

  # All checks finished
  if [ "$total" -gt 0 ] && [ "$pending" -eq 0 ]; then
    break
  fi

  sleep 60
  elapsed=$((elapsed + 60))
done
```

If the loop exits due to timeout, report:

```text
**CI run:** timed out (no checks appeared after 5 minutes)
```

---

## Step 5 — Report result

After CI completes, check for code failures (applying the same skip list
as `scan-bot-prs`):

```bash
gh pr checks PR_NUMBER --repo OWNER/REPO \
  --json name,state --jq '.[] | select(.state == "FAILURE" or .state == "ERROR") | .name'
```

**Skip list** (not code failures):

- `codecov/project`, `codecov/patch`
- `docs/readthedocs.org:*`
- `ack / ack`
- `renovate/stability-days`, `renovate/artifacts`
- `SonarCloud Code Analysis`

### Output format

```text
## Rebase Result

**Repo:** OWNER/REPO
**PR:** #NUMBER — TITLE
**Action taken:** rebased onto BASE_BRANCH / already up to date / conflicts (aborted)
**CI run:** new (triggered by push) / existing (no push, reporting old results)
**CI result:** all passing / N code failures

### Failing checks (if any)

- check_name_1
- check_name_2
```

If all code checks pass: report success. The rebase fixed it.

If code checks still fail: report the failing check names. The
orchestrator will pass these to `diagnose-ci`.
