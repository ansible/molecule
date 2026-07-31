# DevSecOps CI/CD Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add security scanning (deps, SAST, secrets, Actions hardening) plus SBOM + provenance to Molecule's CI/CD so published packages have no known security issues, and make the pipeline skip heavy jobs when irrelevant.

**Architecture:** One new local workflow `security.yml` runs four independent scanners in parallel (pip-audit, bandit, gitleaks, zizmor), each with an auditable allowlist under `.config/security/`. `release.yml` gains a hard security gate (`workflow_call` + `needs`) plus CycloneDX SBOM generation and `actions/attest-build-provenance` for both the PyPI dists and the collection tarball. No upstream `team-devtools` workflow is forked.

**Tech Stack:** GitHub Actions, `uv`/`uvx`, pip-audit, bandit, gitleaks, zizmor, CycloneDX (`cyclonedx-py`), `actions/attest-build-provenance`, tox.

## Global Constraints

- Scope: **local workflows only** — do NOT fork/edit `ansible/team-devtools` reusable workflows (`tox.yml`, `ack.yml`, `finalize.yml`, `push.yml` bodies stay as-is).
- Gating: **fail on any finding**, but every scanner reads a version-controlled allowlist; each allowlist entry MUST carry a justification comment.
- SAST tool: **Bandit only** (no CodeQL, no GHAS).
- Release: **hard gate** — nothing publishes to PyPI/Galaxy if any scan fails.
- All actions in NEW/EDITED workflows MUST be **pinned to a commit SHA** (zizmor `unpinned-uses` is High). Add a trailing `# vX.Y.Z` comment for readability.
- Every job in NEW/EDITED workflows MUST declare a least-privilege `permissions:` block.
- Package manager is `uv`; lockfile is `uv.lock`. Export deps with `uv export --frozen --no-emit-project --no-dev`.
- Python floor 3.10; `default_python` for lint is 3.10.
- Config lives under `.config/security/`; workflows under `.github/workflows/`.
- Verified baseline (2026-08-01): pip-audit = clean, bandit (medium+) = clean, zizmor = 41 findings on EXISTING workflows (mostly upstream `@main` refs + missing `permissions:`).

---

## File Structure

- Create: `.config/security/pip-audit-ignore.txt` — CVE/GHSA ignore list.
- Create: `.config/security/bandit.yaml` — bandit config.
- Create: `.config/security/gitleaks.toml` — gitleaks allowlist/config.
- Create: `.config/security/zizmor.yml` — zizmor config (ignores upstream-imposed findings only).
- Create: `.github/workflows/security.yml` — the security workflow.
- Modify: `.github/workflows/release.yml` — security gate + SBOM + attestation.

---

## Task 1: Security config files

**Files:**
- Create: `.config/security/pip-audit-ignore.txt`
- Create: `.config/security/bandit.yaml`
- Create: `.config/security/gitleaks.toml`
- Create: `.config/security/zizmor.yml`

**Interfaces:**
- Produces: file paths consumed by Task 2 jobs — `.config/security/pip-audit-ignore.txt`, `.config/security/bandit.yaml`, `.config/security/gitleaks.toml`, `.config/security/zizmor.yml`.

- [ ] **Step 1: Create the pip-audit ignore list**

`.config/security/pip-audit-ignore.txt`:

```text
# pip-audit ignore list.
# One vulnerability id (GHSA-… or CVE-…) per line, followed by a
# justification and a review-by date. Entries are passed to pip-audit via
# repeated --ignore-vuln flags. Keep this list EMPTY unless a finding is a
# confirmed false positive or an unfixable upstream transitive CVE.
#
# Example:
# GHSA-xxxx-xxxx-xxxx  # transitive via <dep>, no fix upstream, review 2026-12-01
```

- [ ] **Step 2: Create the bandit config**

`.config/security/bandit.yaml`:

```yaml
---
# Bandit configuration for Molecule SAST.
# Scanned path is passed on the CLI (src). We only exclude test trees.
exclude_dirs:
  - tests
  - .tox
  - .venv
# Skip nothing globally; suppress individual false positives inline with
# `# nosec: <reason>` on the offending line. Add B-ids here only with a
# repo-wide justification.
skips: []
```

- [ ] **Step 3: Create the gitleaks config**

`.config/security/gitleaks.toml`:

```toml
# Gitleaks configuration for Molecule secret scanning.
# Extends the upstream default ruleset, then applies a repo allowlist.
[extend]
useDefault = true

[allowlist]
description = "Molecule repo allowlist — test fixtures contain no real secrets"
paths = [
  '''tests/.*''',
  '''community\.molecule/tests/.*''',
]
# Add specific regexes here ONLY for confirmed false positives, each with a
# comment explaining why the match is not a real secret.
regexes = []
```

- [ ] **Step 4: Create the zizmor config**

`.config/security/zizmor.yml`:

```yaml
---
# Zizmor configuration for GitHub Actions hardening.
# We CANNOT fix findings that originate from the upstream
# `ansible/team-devtools` reusable workflows (they are referenced by @main by
# design and inherit secrets). Those specific findings are ignored here WITH a
# justification. Findings in our own workflow steps must be fixed, not ignored.
rules:
  unpinned-uses:
    ignore:
      # Upstream reusable workflows are referenced by branch by project policy.
      - tox.yml
      - ack.yml
      - finalize.yml
      - push.yml
  secrets-inherit:
    ignore:
      # `secrets: inherit` is required by the team-devtools reusable workflows.
      - tox.yml
      - ack.yml
```

- [ ] **Step 5: Verify configs are syntactically valid**

Run:
```bash
python3 -c "import yaml,sys; [yaml.safe_load(open(f)) for f in ['.config/security/bandit.yaml','.config/security/zizmor.yml']]; print('yaml ok')"
python3 -c "import tomllib; tomllib.load(open('.config/security/gitleaks.toml','rb')); print('toml ok')"
```
Expected: prints `yaml ok` then `toml ok`.

- [ ] **Step 6: Commit**

```bash
git add .config/security/
git commit -m "ci(security): add scanner config and allowlists"
```

---

## Task 2: security.yml workflow

**Files:**
- Create: `.github/workflows/security.yml`
- Test: local runs of each scanner + `actionlint`

**Interfaces:**
- Consumes: the four config files from Task 1.
- Produces: a workflow named `security` with `on: [pull_request, push, schedule, workflow_dispatch, workflow_call]`, four jobs (`deps`, `sast`, `secrets`, `hardening`). Task 3's `release.yml` calls it via `uses: ./.github/workflows/security.yml`.

- [ ] **Step 1: Write the workflow file**

`.github/workflows/security.yml`:

```yaml
---
name: security

on:
  pull_request:
    branches: ["main", "releases/**", "stable/**"]
  push:
    branches: ["main"]
  schedule:
    - cron: "0 3 * * 1" # weekly full scan, Monday 03:00 UTC
  workflow_dispatch:
  workflow_call:

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.sha }}
  cancel-in-progress: true

permissions:
  contents: read

env:
  FORCE_COLOR: "1"

jobs:
  deps:
    name: deps (pip-audit)
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: astral-sh/setup-uv@v6 # pinned below
        with:
          version: "0.11.32"
      - name: Export locked dependencies
        run: uv export --frozen --no-emit-project --no-dev -o requirements.txt
      - name: Build pip-audit ignore args
        id: ignores
        run: |
          set -euo pipefail
          args=""
          while IFS= read -r line; do
            id="${line%%#*}"; id="$(echo "$id" | xargs)"
            [ -z "$id" ] && continue
            args="$args --ignore-vuln $id"
          done < .config/security/pip-audit-ignore.txt
          echo "args=$args" >> "$GITHUB_OUTPUT"
      - name: Audit dependencies
        run: uvx pip-audit -r requirements.txt --strict ${{ steps.ignores.outputs.args }}

  sast:
    name: sast (bandit)
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: astral-sh/setup-uv@v6
        with:
          version: "0.11.32"
      - name: Run bandit
        run: uvx bandit -c .config/security/bandit.yaml -r src -ll

  secrets:
    name: secrets (gitleaks)
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 0
      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@83373cf2f8c4db6e24b41c1a9b086bb9619e9cd3 # v2.3.9
        env:
          GITLEAKS_CONFIG: .config/security/gitleaks.toml
          GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"
          GITLEAKS_ENABLE_SUMMARY: "true"

  hardening:
    name: hardening (zizmor)
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: astral-sh/setup-uv@v6
        with:
          version: "0.11.32"
      - name: Run zizmor
        run: uvx zizmor --config .config/security/zizmor.yml .github/workflows
```

- [ ] **Step 2: Resolve and pin remaining action SHAs**

The `astral-sh/setup-uv@v6` and `gitleaks/gitleaks-action` refs above must be replaced with commit SHAs (zizmor `unpinned-uses` is High and this workflow scans itself). Resolve current SHAs:

```bash
gh api repos/astral-sh/setup-uv/commits/v6 --jq .sha
gh api repos/gitleaks/gitleaks-action/commits/v2 --jq .sha
```
Replace each `uses:` line with `owner/repo@<sha> # <tag>`. If `gh` is unavailable, look up the release tag's commit on GitHub. The `checkout` and `gitleaks` SHAs above are already pinned; verify they resolve.

- [ ] **Step 3: Lint the workflow**

Run:
```bash
uvx --from actionlint actionlint .github/workflows/security.yml || uvx actionlint .github/workflows/security.yml
```
Expected: no errors. (If actionlint isn't packaged for uvx, use the pre-commit hook: `prek run actionlint --files .github/workflows/security.yml`.)

- [ ] **Step 4: Run each scanner locally to confirm green**

Run:
```bash
uv export --frozen --no-emit-project --no-dev -o /tmp/reqs.txt
uvx pip-audit -r /tmp/reqs.txt --strict
uvx bandit -c .config/security/bandit.yaml -r src -ll
uvx zizmor --config .config/security/zizmor.yml .github/workflows
```
Expected: pip-audit "No known vulnerabilities found"; bandit no issues at medium+; zizmor reports 0 findings for OUR workflows (upstream ones suppressed by config). If zizmor still flags `security.yml`/`release.yml` steps, FIX those steps (add `permissions:`, pin SHAs) — do not add them to the ignore config.

- [ ] **Step 5: Run zizmor to self-check the new workflow specifically**

Run:
```bash
uvx zizmor --config .config/security/zizmor.yml .github/workflows/security.yml
```
Expected: 0 findings. If any, fix inline.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/security.yml
git commit -m "ci(security): add parallel scanning workflow"
```

---

## Task 3: release.yml — security gate, SBOM, attestation

**Files:**
- Modify: `.github/workflows/release.yml`

**Interfaces:**
- Consumes: `security.yml` from Task 2 (via `uses: ./.github/workflows/security.yml`).
- Produces: a `security` gate job; `release` and `publish-collection` jobs gated on it; SBOM artifacts + build provenance attestations for the wheel/sdist and the collection tarball.

- [ ] **Step 1: Read the current release.yml**

Run: `sed -n '1,120p' .github/workflows/release.yml` and note the three existing jobs: `release`, `publish-collection`, `forum_post`, and the top-level `on:` block.

- [ ] **Step 2: Add a top-level permissions block and the security gate job**

Below the `on:` block (before `jobs:`), add:

```yaml
permissions:
  contents: read
```

As the FIRST entry under `jobs:`, add:

```yaml
  security:
    uses: ./.github/workflows/security.yml
    permissions:
      contents: read
```

- [ ] **Step 3: Gate the publish jobs on security**

In the `release` job, add `needs: [security]` and, in the `publish-collection` job, add `needs: [security]` (immediately under the `if:` line of each). This makes both jobs wait for and require the scans.

- [ ] **Step 4: Add SBOM + attestation to the `release` (PyPI) job**

In the `release` job, add `attestations: write` to its `permissions:` block (it already has `id-token: write`). After the `Build dists` step and BEFORE `Publish to pypi.org`, insert:

```yaml
      - name: Generate SBOM for dists
        run: |
          uvx --from cyclonedx-bom cyclonedx-py environment \
            --output-format json --outfile dist/sbom.cdx.json || \
          uvx cyclonedx-py environment -o dist/sbom.cdx.json
      - name: Attest build provenance for dists
        uses: actions/attest-build-provenance@<PIN_SHA> # v2
        with:
          subject-path: "dist/*.tar.gz, dist/*.whl"
      - name: Upload SBOM artifact
        uses: actions/upload-artifact@<PIN_SHA> # v4
        with:
          name: sbom-dists
          path: dist/sbom.cdx.json
```

Resolve the two `<PIN_SHA>` values with:
```bash
gh api repos/actions/attest-build-provenance/commits/v2 --jq .sha
gh api repos/actions/upload-artifact/commits/v4 --jq .sha
```

- [ ] **Step 5: Add SBOM + attestation to the `publish-collection` job**

Change that job's `permissions:` to:
```yaml
    permissions:
      contents: read
      id-token: write
      attestations: write
```
After the `Build the collection` step and BEFORE `Publish the collection on Galaxy`, insert:

```yaml
      - name: Generate SBOM for collection
        run: |
          uvx --from cyclonedx-bom cyclonedx-py requirements \
            community.molecule/requirements.txt \
            -o community.molecule-sbom.cdx.json || true
      - name: Attest collection tarball provenance
        uses: actions/attest-build-provenance@<PIN_SHA> # v2
        with:
          subject-path: "./community.molecule-*.tar.gz"
      - name: Upload collection SBOM artifact
        uses: actions/upload-artifact@<PIN_SHA> # v4
        with:
          name: sbom-collection
          path: community.molecule-sbom.cdx.json
```
Use the same resolved SHAs as Step 4.

- [ ] **Step 6: Lint the edited workflow**

Run:
```bash
uvx zizmor --config .config/security/zizmor.yml .github/workflows/release.yml
prek run actionlint --files .github/workflows/release.yml || uvx actionlint .github/workflows/release.yml
```
Expected: actionlint clean; zizmor 0 findings for release.yml (the `@main` upstream rule doesn't apply here since release.yml uses pinned/local refs). Fix any real findings inline.

- [ ] **Step 7: Verify SBOM generation works locally**

Run:
```bash
uvx cyclonedx-py requirements community.molecule/requirements.txt -o /tmp/coll-sbom.cdx.json && python3 -c "import json;d=json.load(open('/tmp/coll-sbom.cdx.json'));print('sbom components:',len(d.get('components',[])))"
```
Expected: prints a component count (>=1). If the `cyclonedx-py` subcommand differs by version, adjust the command in the workflow to match and re-verify.

- [ ] **Step 8: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci(release): gate on security scans, add SBOM + provenance attestation"
```

---

## Task 4: Speed — path filters for heavy jobs

**Files:**
- Modify: `.github/workflows/security.yml`

**Interfaces:**
- Consumes: the `security.yml` from Task 2.
- Produces: `deps` and `sast` jobs that are skipped on docs-only changes; `secrets` and `hardening` always run.

- [ ] **Step 1: Add a change-detection gate job**

At the top of `jobs:` in `security.yml`, add:

```yaml
  changes:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    outputs:
      code: ${{ steps.filter.outputs.code }}
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: dorny/paths-filter@<PIN_SHA> # v3
        id: filter
        with:
          filters: |
            code:
              - 'src/**'
              - 'community.molecule/**'
              - 'uv.lock'
              - 'pyproject.toml'
              - '.github/workflows/**'
              - '.config/security/**'
```
Resolve the SHA: `gh api repos/dorny/paths-filter/commits/v3 --jq .sha`.

- [ ] **Step 2: Gate deps and sast on code changes**

Add to both the `deps` and `sast` jobs:
```yaml
    needs: [changes]
    if: ${{ needs.changes.outputs.code == 'true' || github.event_name != 'pull_request' }}
```
(On non-PR events — push, schedule, workflow_call from release — they always run.)

- [ ] **Step 3: Lint and self-check**

Run:
```bash
prek run actionlint --files .github/workflows/security.yml || uvx actionlint .github/workflows/security.yml
uvx zizmor --config .config/security/zizmor.yml .github/workflows/security.yml
```
Expected: clean.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/security.yml
git commit -m "ci(security): skip deps/sast scans on docs-only PRs"
```

---

## Task 5: Documentation

**Files:**
- Create: `.config/security/README.md`

**Interfaces:**
- Consumes: nothing at runtime.
- Produces: contributor-facing docs for the allowlist/ignore workflow.

- [ ] **Step 1: Write the README**

`.config/security/README.md`:

```markdown
# Security scanning config

The `security` GitHub Actions workflow runs four scanners on every PR and push,
and gates releases. All findings fail the build. When a finding is a confirmed
false positive or an unfixable upstream issue, add an allowlist entry HERE with
a justification — never disable the scanner.

| Scanner | Tool | Allowlist file |
|---------|------|----------------|
| Dependencies | pip-audit | `pip-audit-ignore.txt` (one CVE/GHSA id + reason per line) |
| SAST | bandit | `bandit.yaml` (`skips:`) or inline `# nosec: <reason>` |
| Secrets | gitleaks | `gitleaks.toml` (`[allowlist]`) |
| Actions hardening | zizmor | `zizmor.yml` (`rules.*.ignore`) |

Every allowlist entry MUST include why it is safe and, where relevant, a
review-by date. Prefer fixing the code/dependency over allowlisting.

Run locally before pushing:

    uv export --frozen --no-emit-project --no-dev -o /tmp/reqs.txt
    uvx pip-audit -r /tmp/reqs.txt --strict
    uvx bandit -c .config/security/bandit.yaml -r src -ll
    uvx zizmor --config .config/security/zizmor.yml .github/workflows
```

- [ ] **Step 2: Commit**

```bash
git add .config/security/README.md
git commit -m "docs(security): document scanner allowlist workflow"
```

---

## Self-Review notes

- **Spec coverage:** dependency scanning → Task 2 `deps`; SAST → Task 2 `sast`; secrets → Task 2 `secrets`; Actions hardening → Task 2 `hardening`; SBOM + signing → Task 3 (SBOM + attest-build-provenance); fail-on-any-with-allowlist → Task 1 configs + `--strict`/`-ll`; hard release gate → Task 3 `needs: [security]`; speed (parallel) → Task 2 independent jobs; speed (path filters) → Task 4; verify locally → verification steps in Tasks 2/3.
- **Placeholders:** `<PIN_SHA>` markers are intentional and each has an adjacent `gh api … --jq .sha` command to resolve them; not free-text TODOs.
- **Type/name consistency:** workflow name `security`; job ids `changes`/`deps`/`sast`/`secrets`/`hardening` used consistently across Tasks 2–4; config paths identical everywhere.
```
