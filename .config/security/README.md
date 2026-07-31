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
