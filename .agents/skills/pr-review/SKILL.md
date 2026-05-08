---
name: pr-review
description: >
  Use when handling pull request reviews, including automated (Copilot) and
  human reviewer feedback. Use when responding to PR comments, resolving
  review threads, or updating PRs after review.
argument-hint: "<PR number>"
user-invocable: true
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# PR Review

This skill defines how to handle PR review feedback in this project.

## Responding to review comments

Every review comment MUST receive a response. Resolve threads only after the
feedback has been addressed and accepted; leave threads unresolved when disputing
feedback and escalate to a human reviewer. Unanswered comments or unresolved
disputed threads block merge.

### Rules

- Address ALL review comments before requesting re-review. Do not leave
  comments unanswered.
- Every comment requires a **closing reply**. When the feedback is addressed
  or accepted, also **resolve the thread** via the GitHub UI or API. When
  disputing or flagging a false positive, leave the thread unresolved for
  human escalation.
- Reply to each comment with a **brief explanation of how it was resolved** and
  the commit hash (e.g., "Removed the unused imports so Ruff F401 passes.
  Fixed in abc1234."). Do not reply with only the SHA; explain the fix.
- If a comment is a false positive or you disagree, reply with a clear
  technical explanation. Do not resolve the thread. This will require human
  intervention. Do not dismiss without justification.
- After pushing fixes, update the PR description to reflect the expanded scope
  (per the pr-new skill).

### Deferred work MUST be tracked

Any time a review response includes language like "follow-up PR", "subsequent
PR", "leaving as a follow-up", "future enhancement", "out of scope for this
PR", or "logging this for later" — you **MUST** create a GitHub issue
immediately using `gh issue create`. Do not reply to the comment without also
creating the issue. Include the issue URL in your reply so the reviewer can
verify tracking.

Untracked follow-ups are invisible debt. If it is worth mentioning, it is
worth an issue.

```bash
gh issue create --repo <upstream-owner>/<repo> \
  --title "<type>(scope): <brief description>" \
  --body "$(cat <<'EOF'
## Context

<What was the review comment and why it wasn't addressed in this PR>

Flagged in: <link to PR comment thread>

## Proposal

<What should be done>

## References

- PR #N
EOF
)"
```

## Copilot review patterns

Copilot automated reviews surface recurring categories. Address these
proactively before pushing to avoid review round-trips:

### Supply-chain security

Pin GitHub Actions to commit SHAs instead of mutable tags (`@v1`). Mutable
tags allow upstream changes to affect CI without review. Use a comment to
note the original tag:

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4
```

### Inaccurate documentation

Documentation MUST accurately describe the actual behavior. If a workflow
triggers on `pull_request` targeting `main`, don't document it as running
on "every pull request". Be specific about triggers, branches, and conditions.

### Markdown table formatting

Tables must use a single leading `|` on each line. Double leading `||` renders
as an extra empty column. Validate table rendering before committing.

### Inaccurate comments

Code comments and docstrings MUST accurately describe what the code does. If
you rename a function, change behavior, or remove functionality, update all
associated comments in the same commit.

### Secrets in documentation

Never show API keys, tokens, or credentials on command lines in docs or
examples. Demonstrate env var usage instead. Shell history and process lists
expose command-line arguments.

### Unused imports (Ruff F401)

Copilot often flags unused imports. With Ruff `F` rules enabled, these fail CI.
Remove unused imports or use the symbol (e.g. in a type annotation or
assertion). Prefer trimming the import list over `# noqa: F401` unless the
import is intentionally side-effect only.

## Workflow

1. **Ensure the PR branch is up to date with upstream main.** Before
   reviewing or pushing fixes, rebase or merge `upstream/main` into the PR
   branch. A stale base causes misleading CI results, merge conflicts, and
   wasted review cycles. If the branch is behind, update it first:

   ```bash
   git fetch upstream
   git rebase upstream/main   # or: git merge upstream/main
   git push --force-with-lease
   ```

2. After pushing a PR, wait for both CI and Copilot review.
3. Check CI status and read all review comments.
4. Fix all issues in a single commit (or minimal commits).
5. Reply to each comment with a brief explanation of how it was resolved and
   the commit hash (e.g., "Removed unused imports. Fixed in abc1234.").
6. **Reply to every comment.** Resolve the thread only when the issue is
   addressed or accepted. Leave disagreement or false-positive threads open
   for a human reviewer to decide.

### Checking CI status

Always check CI checks as part of the review workflow. Fix failures before
addressing review comments — a green build is a prerequisite for merge.

```bash
# List failing checks (replace N with PR number)
gh pr checks N --json name,state --jq '.[] | select(.state != "SUCCESS" and .state != "PENDING")'

# Get the log link for a specific failed check
gh pr checks N --json name,state,link --jq '.[] | select(.name == "CHECK_NAME") | .link'

# View failed job logs directly
gh run view RUN_ID --log-failed 2>&1 | tail -80
```

Common CI failures and how to fix them:

- **prek (ruff)**: Run `tox -e lint` to reproduce. Long type annotations
  and function signatures often need line wrapping.
- **prek (mypy)**: Add type annotations to all new functions. Use the correct
  `type: ignore` code (e.g., `[assignment]` vs `[method-assign]`). Run
  `tox -e lint` to verify.
- **prek (biome)**: Run `tox -e lint` to reproduce. Biome enforces formatting
  for JSON, Markdown, and JavaScript files.
- **prek (ansible-lint)**: Run `tox -e lint` to reproduce. Ensure playbooks
  and roles follow ansible-lint rules.
- **prek (tombi)**: Run `tox -e lint` to reproduce. TOML files must be
  formatted with tombi.
- **test failures**: Run `tox -e py` to reproduce. Update tests when behavior
  changes.

Do **not** run `ruff`, `mypy`, `pytest`, or `prek` directly — always use tox.
See the `/tox` skill for the full environment reference.

### Replying to review comments

Post a reply using the REST API. Each reply must state **how** the issue was
resolved and include the commit hash (not only the SHA):

```bash
gh api -X POST "repos/<upstream-owner>/<repo>/pulls/PR/comments/COMMENT_ID/replies" \
  -f body="Removed the unused imports so Ruff F401 passes. Fixed in COMMIT_SHA."
```

To get comment IDs: `gh api repos/<upstream-owner>/<repo>/pulls/PR/comments` and
use each comment's `id`. Alternatively, reply in the GitHub PR UI, then resolve
threads via GraphQL below.

### Resolving review threads (GraphQL)

**IMPORTANT:** Always use `resolveReviewThread` to resolve threads. Do NOT use
`minimizeComment` — that hides the comment text but does NOT resolve the review
thread, leaving it as an unresolved conversation on the PR.

Replace `N` with the PR number and `THREAD_ID` with the `id` from
`reviewThreads.nodes[].id` (from the list query). Filter nodes where
`isResolved` is false if you only want to resolve open threads.

```bash
# List unresolved threads (replace OWNER/REPO with actual values)
gh api graphql -f query='{
  repository(owner: "<upstream-owner>", name: "<repo>") {
    pullRequest(number: N) {
      reviewThreads(first: 50) {
        nodes { id isResolved comments(first:1) { nodes { body } } }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | {id, snippet: .comments.nodes[0].body[0:120]}'

# Resolve one thread
gh api graphql -f query='mutation {
  resolveReviewThread(input: {threadId: "THREAD_ID"}) {
    thread { isResolved }
  }
}'

# Resolve multiple threads in a loop
for tid in "THREAD_ID_1" "THREAD_ID_2"; do
  gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \"${tid}\"}) { thread { isResolved } } }"
done
```

1. Update the PR description to include the new commit(s).
2. If CI failure is unrelated to your changes (e.g., flaky test, transient
   network issue), fix it anyway — the PR owns the green build.

### After pushing fixes: check for a new Copilot review

Copilot may run again on new commits. Re-check whether it left a new review or
line comments so you can reply and resolve any new threads.

```bash
# New Copilot review (replace N with PR number, ISO8601 with last push time)
gh api repos/<upstream-owner>/<repo>/pulls/N/reviews --jq '.[] | select(.user.login == "copilot-pull-request-reviewer[bot]" and .submitted_at > "ISO8601") | {submitted_at, state, body: .body[0:200]}'

# New Copilot line comments (replace N and ISO8601)
gh api repos/<upstream-owner>/<repo>/pulls/N/comments --jq '.[] | select(.user.login == "Copilot" and .created_at > "ISO8601") | {id, created_at, path, body: .body[0:150]}'
```

If both return nothing, no new Copilot activity. Otherwise, address new
comments (reply with how it was resolved + commit hash, then resolve threads)
and repeat this check after the next push.
