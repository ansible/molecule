# DevSecOps CI/CD Hardening — Design

Date: 2026-08-01
Repo: `ansible-community/molecule` (this workspace)
Status: Approved design → implementation

## Goal

Improve the existing CI/CD pipelines to meet DevSecOps best practices and
repository policies so that:

1. Published packages (the PyPI sdist/wheel and the `community.molecule`
   Ansible collection tarball) have **no known security issues**.
2. The pipelines run **faster** (no serial security overhead; skip heavy jobs
   when irrelevant).

## Current state (as-is)

- `.github/workflows/`:
  - `tox.yml` → calls `ansible/team-devtools/.github/workflows/tox.yml@main`
    (8 coverage jobs + `collection` + `eco` across a Python matrix). Has
    `concurrency` + `cancel-in-progress`.
  - `release.yml` → builds dists via `tox -e pkg`, publishes to PyPI via
    trusted publishing (OIDC, `id-token: write`), builds & publishes the
    `community.molecule` collection to Galaxy, posts a forum announcement.
  - `push.yml`, `ack.yml`, `finalize.yml`, `redirects.yml` → thin wrappers
    around `team-devtools` reusable workflows.
- `.pre-commit-config.yaml`: has `detect-private-key`, `actionlint`, `ruff`,
  `mypy`, `pylint`, `codespell`, `yamllint`, `uv-lock`. Good linting baseline.
- Package manager: `uv` (lockfile `uv.lock`). `tox -e pkg` builds dists.
- **No security scanning exists**: no dependency CVE scan, no SAST, no secret
  scanning gate in CI, no GitHub Actions hardening audit, no SBOM, no artifact
  provenance/attestation.

## Decisions (from brainstorming)

- **Scope:** Local workflows only. Do **not** fork/vendor the `team-devtools`
  reusable workflows. Add new local workflow(s) and edit `release.yml`.
- **Controls:** dependency scanning, SAST, supply-chain (SBOM + signing),
  secret + workflow hardening — all four.
- **Speed:** caching, path filters/conditional jobs, parallelism tuning, and
  security jobs run in parallel with existing tests.
- **Gating:** fail on any finding, **with** an auditable, version-controlled
  ignore/allowlist (justification required) so the pipeline is not permanently
  red on genuinely unfixable upstream transitive CVEs.
- **SAST tool:** Bandit only (no CodeQL / no GHAS dependency).
- **Release gate:** hard gate — `release.yml` runs the security scans first and
  refuses to publish to PyPI/Galaxy if any scan fails.

## Architecture

### 1. New workflow: `.github/workflows/security.yml`

Triggers: `pull_request`, `push` (main), `schedule` (weekly full scan),
`workflow_dispatch`, and `workflow_call` (so `release.yml` can gate on it).

`concurrency` group + `cancel-in-progress` (mirrors `tox.yml`).

Top-level `permissions: contents: read` (least privilege); jobs that upload
SARIF add `security-events: write` only where needed.

Independent parallel jobs (each pins actions to commit SHAs):

| Job | Tool | Runs on | Behavior |
|-----|------|---------|----------|
| `deps` | `pip-audit` (via `uvx`) against `uv.lock` and the collection requirements | code/lock changes | Fail on any vuln; ignores read from `.config/security/pip-audit-ignore.txt` |
| `sast` | `bandit` (via `uvx`) recursive over `src/` | code changes | Fail on any finding at/above configured severity; config `.config/security/bandit.yaml`; per-line `# nosec: <reason>` allowed |
| `secrets` | `gitleaks` | PR: diff scan; schedule/push: full history | Fail on any leak; allowlist `.config/security/gitleaks.toml` |
| `hardening` | `zizmor` (via `uvx`) over `.github/workflows/` | workflow changes | Fail on any finding; config `.config/security/zizmor.yml` |

Path filters: docs-only changes (`docs/**`, `*.md`, `mkdocs.yml`) do not
trigger `deps`/`sast`; `secrets`/`hardening` still run (cheap). This is the
"skip heavy jobs" speedup.

### 2. Supply-chain: SBOM + attestation in `release.yml` (edits)

- Add a `security` gate: `release.yml` calls `./.github/workflows/security.yml`
  via `workflow_call`; both `release` and `publish-collection` gain
  `needs: [security]` so nothing publishes on a red scan.
- In the `release` job (PyPI): after `tox -e pkg`, generate a CycloneDX SBOM for
  the built dists and run `actions/attest-build-provenance` on the sdist+wheel
  (uses existing `id-token: write`). Attach SBOM to the release.
- In `publish-collection`: after `ansible-galaxy collection build`, generate a
  CycloneDX SBOM from the collection's Python requirements and attest the
  tarball. Attach SBOM to the release.

### 3. Speed

- Security jobs are short and fully parallel → negligible addition to the tox
  critical path.
- Path filters skip `deps`/`sast` on docs-only PRs.
- `fail-fast` semantics: each job fails independently and early.
- `uvx` tool runs are cached via `astral-sh/setup-uv` cache; `gitleaks`/`zizmor`
  pinned-action installs are cached by their actions.
- We intentionally do **not** touch the upstream 8-coverage-job tox fan-out
  (out of scope: local-only). Path filters ensure security does not pile onto
  it.

### 4. Config surface: `.config/security/`

- `pip-audit-ignore.txt` — one CVE/GHSA id per line + `# reason (expiry)`.
- `bandit.yaml` — bandit config (severity/confidence thresholds, excludes).
- `gitleaks.toml` — gitleaks allowlist (regexes/paths + reason).
- `zizmor.yml` — zizmor config (ignored rules + reason).

Empty/minimal to start; entries added only for verified false positives or
genuinely unfixable upstream issues, each with a justification.

## Verification (local, before finalize)

Run each scanner locally via `uvx`/pinned binaries and make the repo pass:

- `uvx pip-audit -r <exported reqs>` / against `uv.lock`
- `uvx bandit -c .config/security/bandit.yaml -r src`
- `gitleaks detect --no-banner` (or `uvx`-equivalent) on the working tree
- `uvx zizmor .github/workflows`
- `uvx cyclonedx-py` (or `cyclonedx-bom`) SBOM generation smoke test
- `actionlint` on the new/edited workflows

Fix real findings in code/config; record allowlist entries (with reasons) for
any confirmed unfixable transitive CVEs so CI lands green.

## Deliverables

- `.github/workflows/security.yml` (new)
- `.github/workflows/release.yml` (edited: security gate, SBOM, attestation)
- `.config/security/{pip-audit-ignore.txt,bandit.yaml,gitleaks.toml,zizmor.yml}`
- This design doc.

## Non-goals

- Forking/modifying `team-devtools` reusable workflows.
- CodeQL / GitHub Advanced Security.
- Changing the upstream tox coverage-job fan-out.
- Container image scanning of Molecule's test-target images (Molecule drives
  user-supplied images at test time; not a published artifact).
