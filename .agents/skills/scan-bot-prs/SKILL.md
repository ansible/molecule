---
name: scan-bot-prs
description: >
  Scan Ansible devtools repos for open PRs from renovate and dependabot,
  check their CI status, and produce a prioritized list of failing PRs.
  Use to get a quick overview of which bot PRs need attention.
argument-hint: "[repo]"
user-invocable: true
type: skill
mandatory: false
triggers:
  - "scan bot PRs"
  - "list failing bot PRs"
  - "check renovate PRs"
  - "check dependabot PRs"
  - "show broken dependency PRs"
metadata:
  author: Ansible DevTools Team
  version: 1.1.0
---

# Scan Bot PRs

Scan Ansible devtools repositories for open dependency update PRs from
renovate and dependabot. Check CI status for each. Output a prioritized
table of failing PRs that need fixing.

This skill is **read-only** — it does not modify any repository or PR.

---

## Input

- **No arguments**: scan all target repos.
- **Single repo** (e.g., `ansible/vscode-ansible`): scan only that repo.

---

## Entry Gate

```bash
gh auth status
```

If not authenticated, stop.

---

## Step 1 — Resolve target repos

Fetch the canonical repo list from `ansible/team-devtools`:

```bash
gh api repos/ansible/team-devtools/contents/config/repos.lst \
  --jq '.content' | base64 -d
```

If unavailable or if a specific repo was passed as argument, use the
argument or fall back to:

```text
ansible/vscode-ansible
ansible/ansible-dev-tools
ansible/ansible-navigator
ansible/ansible-lint
ansible/ansible-compat
ansible/ansible-creator
ansible/ansible-dev-environment
ansible/ansible-sign
ansible/molecule
ansible/tox-ansible
ansible/pytest-ansible
ansible/mkdocs-ansible
ansible/team-devtools
ansible/actions
ansible/ansible-content-actions
ansible-automation-platform/ansible-devtools-container
ansible-automation-platform/ansible-devspaces-container
```

---

## Step 2 — Discover open bot PRs

For each repo, run **two separate queries** (gh does not support multiple
`--author` in one call):

```bash
gh pr list --repo OWNER/REPO --author "app/renovate" --state open \
  --json number,title,headRefName,url,labels,createdAt

gh pr list --repo OWNER/REPO --author "app/dependabot" --state open \
  --json number,title,headRefName,url,labels,createdAt
```

Merge both result sets per repo.

---

## Step 3 — Filter to failing PRs

For each discovered PR, check CI status:

```bash
gh pr checks PR_NUMBER --repo OWNER/REPO \
  --json name,state --jq '[.[] | select(.state == "FAILURE" or .state == "ERROR")]'
```

**Skip list** — these checks do not count as code failures:

- `codecov/project`, `codecov/patch`
- `docs/readthedocs.org:*`
- `ack / ack`
- `renovate/stability-days`
- `renovate/artifacts`
- `SonarCloud Code Analysis`

**A PR is failing** if it has at least one `FAILURE` or `ERROR` that is
NOT in the skip list. Drop everything else — this skill only outputs
failing PRs.

---

## Step 4 — Prioritize

Rank failing PRs in this order:

1. **Security updates** — title contains `[SECURITY]`, `[security]`, or
   `vulnerability`, or labels include `security`.
2. **Lock file maintenance** — title contains `lock file maintenance`.
   Smallest blast radius, highest fix success rate.
3. **Single dependency updates** — title updates one specific package.
4. **All dependencies updates** — title contains `update all dependencies`.
   Largest blast radius, hardest to fix.

Within each priority tier, sort by **oldest first** (earliest `createdAt`).

---

## Step 5 — Output

### Summary line

```text
Found N failing bot PRs across M repos.
```

### Failing PRs table (sorted by priority)

```text
| Priority | Repo                   | PR#  | Branch                      | Title                          | Failing Checks           | Age   |
|----------|------------------------|------|-----------------------------|--------------------------------|--------------------------|-------|
| SECURITY | ansible/ansible-lint   | 5014 | renovate/security           | fix(security): update deps     | tox/check, tox/lint      | 34d   |
| LOCKFILE | ansible/vscode-ansible | 2716 | renovate/lock-file-maint... | chore(deps): lock file maint.  | preflight, test (linux)  | 30d   |
| SINGLE   | ansible/vscode-ansible | 2756 | renovate/node-24.x          | chore(deps): update node.js    | test (linux), test (wsl) | 18d   |
| ALL      | ansible/molecule       | 4621 | renovate/all                | chore(deps): update all deps   | tox/check, tox/lint      | 45d   |
```

If no failing bot PRs are found, report that and stop.

---

## Error Handling

- If a repo returns a 404 or permission error, skip it and note in output.
- If no bot PRs are found across all repos, report that cleanly.
