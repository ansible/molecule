---
name: architecture-diagram
description: >
  Generate professional C4 architecture diagrams of the Ansible Dev Tools
  ecosystem by cloning and introspecting actual repos. Produces PNG output
  for the AAP Miro board. Use when the user says 'architecture diagram',
  'C4 diagram', 'generate diagram', 'update architecture', or references
  AAP-77196.
argument-hint: "[level=context|container|component|all]"
user-invocable: true
type: workflow
mandatory: false
triggers:
  - "architecture diagram"
  - "C4 diagram"
  - "generate diagram"
  - "update architecture"
  - "AAP-77196"
metadata:
  author: Ansible DevTools Team
  version: 1.0.0
---

# Architecture Diagram Generator

Generate professional C4 architecture diagrams of the Ansible Dev Tools
ecosystem. Diagrams are built from **actual repo introspection** — not
documentation — to ensure accuracy.

## Prerequisites

Before running, ensure these are available:

```bash
python3 --version   # >= 3.10
java -version       # or: plantuml --version
git --version
pip show c4-diagrams  # >= 0.5.2, install with: pip install c4-diagrams
```

If `c4-diagrams` is not installed:

```bash
pip install c4-diagrams
```

PlantUML rendering requires Java. If Java is not present:

```bash
# Fedora / RHEL
sudo dnf install java-17-openjdk
# macOS
brew install plantuml
```

## Workflow

### Step 1: Clone and crawl repos

Clone all ADT ecosystem repos fresh into `/tmp` and introspect their
actual dependency files. This is the foundation — never skip it.

```bash
python3 scripts/crawl_repos.py --clone-dir /tmp/adt-c4-repos --output .architecture-diagrams/dependencies.json
```

This clones 19 repos (shallow, default branch) and reads:
- `pyproject.toml` for Python inter-project dependencies
- `package.json` for TypeScript/Node dependencies
- `Containerfile` / `Dockerfile` for container image builds
- `.github/workflows/*.yml` for container publishing and reusable workflows
- Source code (vscode-ansible) for Python CLI tool spawns, language server, MCP server

Output: `.architecture-diagrams/dependencies.json`

### Step 2: Review crawl results

Read `.architecture-diagrams/dependencies.json` and validate:

1. Are all expected inter-project dependencies captured?
2. Were container builds discovered in GitHub Actions workflows?
3. Did the vscode-ansible crawl find the language server and MCP server?
4. Did the abbenay crawl discover all sub-packages?
5. Did the APME crawl find the Abbenay dependency?

If the crawler missed a known relationship, the agent should note it for
manual addition to the generated diagram code before rendering.

### Step 3: Generate diagram code

```bash
python3 scripts/generate_diagram.py --input .architecture-diagrams/dependencies.json --output-dir .architecture-diagrams --level all
```

Levels:
- `context` — L1 System Context (personas, systems, external deps)
- `container` — L2 Container (individual projects with dependency arrows)
- `component` — L3 Component (per-repo deep dive)
- `all` — generate all levels

For a single repo's component diagram:

```bash
python3 scripts/generate_diagram.py --level component --component-repo ansible/vscode-ansible
```

### Step 4: Review and refine diagram code

Before rendering, the agent SHOULD review the generated `.py` files in
`.architecture-diagrams/` and make refinements:

- Adjust layout by changing `Rel` to `RelDown`, `RelRight`, etc.
- Add missing relationships the crawler could not infer
- Improve labels and descriptions
- Ensure the provenance footer is present

### Step 5: Render to PNG

```bash
python3 scripts/render.py --input-dir .architecture-diagrams --renderer plantuml
```

Output: PNG files in `.architecture-diagrams/`

### Step 6: Present results

Show the user the PNG file paths. The user can then paste them into the
Miro board or include them in documentation.

---

## Repos Crawled

### ADT Primary Projects (10 repos)

| Repo | Language | Notes |
|------|----------|-------|
| `ansible/ansible-dev-tools` | Python | Meta-package + container image builds |
| `ansible/ansible-lint` | Python | Linter |
| `ansible/ansible-compat` | Python | Shared compatibility library |
| `ansible/ansible-navigator` | Python | TUI for execution environments |
| `ansible/ansible-dev-environment` | Python | Virtual env manager (ade) |
| `ansible/ansible-creator` | Python | Scaffolding tool |
| `ansible/ansible-sign` | Python | Content signing |
| `ansible/molecule` | Python | Functional test runner |
| `ansible/vscode-ansible` | TypeScript | VS Code extension (see special handling below) |
| `ansible/team-devtools` | Mixed | Meta-repo (shared CI, skills, config) |

### ADT Experimental / Testing / Community (5 repos)

| Repo | Notes |
|------|-------|
| `ansible/pytest-ansible` | Pytest plugin |
| `ansible/tox-ansible` | Tox plugin |
| `ansible/actions` | Shared GitHub Actions |
| `ansible/ansible-content-actions` | Marketplace actions |
| `ansible/mkdocs-ansible` | MkDocs theme |

### AAP Downstream Container Repos (2 repos)

| Repo | Notes |
|------|-------|
| `ansible-automation-platform/ansible-devtools-container` | Downstream devtools container — packages ADT web server |
| `ansible-automation-platform/ansible-devspaces-container` | Downstream devspaces container |

### Abbenay — AI Daemon (1 repo)

| Repo | Notes |
|------|-------|
| `redhat-developer/abbenay` | Unified AI daemon and library for LLM providers |

Abbenay is a TypeScript monorepo producing:
- `@abbenay/core` — LLM engine abstraction library
- `@abbenay/daemon` — gRPC server, web dashboard, CLI, VS Code backchannel
- VS Code extension (in `packages/vscode/`)
- Python gRPC client (in `packages/python/`)
- Containerized deployment (root `Containerfile`)

**Key relationship:** APME depends on Abbenay for AI-assisted remediation.

### AAP Portal — External Consumer (not crawled)

The AAP Portal is a custom Backstage instance for AAP self-service. It is
NOT a devtools-owned project and is not included in the repo manifest. It
appears in diagrams as an external system (`SystemExt`/`ContainerExt`) with
two key relationships:
- Consumes the ADT web server packaged in the downstream devtools container
- Consumes the ADT Python packages' REST API

### APME — Adjacent Consumer (1 repo)

| Repo | Notes |
|------|-------|
| `ansible/apme` | Multi-validator static analysis platform for Ansible content |

APME is NOT owned by DevTools but is a significant consumer:
- Depends on Abbenay for AI-assisted remediation (Tier 2 escalation)
- Likely depends on ansible-lint (confirm from `pyproject.toml`)
- Components: CLI, engine, validators, daemon, gateway, Galaxy Proxy, React frontend
- Has own containers, Helm chart, bootc VM deployment

---

## Special Crawling Instructions

### vscode-ansible

The VS Code extension is the most architecturally complex single repo.
The crawler MUST discover:

1. **Python CLI tool dependencies** — the extension spawns: `ansible-lint`,
   `ansible-navigator`, `ansible-creator`, `ansible-dev-environment`, and
   potentially others. The crawler searches source code for process spawn
   calls, command references, and configuration settings.

2. **Language Server** — the extension contains an integrated Ansible Language
   Server (previously `ansible/ansible-language-server`, now merged). Find
   `LanguageClient`, `createConnection`, or `LanguageServer` references.

3. **MCP Server** (`packages/ansible-mcp-server/`) — the extension ships
   a bundled MCP server (`@ansible/ansible-mcp-server`) that wraps ADT CLI
   tools for AI agent consumption. The crawler inspects its `src/tools/`
   directory for spawned Python CLI tools (e.g., `ansible-lint`,
   `ansible-navigator`, `ansible-creator`, `ade`, `ansible-builder`).

4. **Package dependencies** — `package.json` deps that map to other ADT projects.

### Abbenay

Crawl `packages/` monorepo structure for sub-packages. Each directory
under `packages/` with a `package.json` is a separate component. Also
discover the root `Containerfile` and `proto/` gRPC definitions.

Note: Abbenay does NOT consume the downstream devtools container. That
relationship belongs to the AAP Portal (Backstage), which is a separate
external system.

### APME

Crawl `pyproject.toml` for Python deps (especially abbenay, ansible-lint).
Discover components from the project structure:
- `src/apme_engine/` — CLI, engine, validators, daemon, remediation
- `src/apme_gateway/` — FastAPI API gateway
- `src/galaxy_proxy/` — Galaxy PEP 503 proxy
- `frontend/` — React operator UI
- `containers/` — container topology
- `proto/` — gRPC service definitions

---

## Diagram Provenance

Every generated diagram includes a footer/subtitle:

> Generated by architecture-diagram skill —
> https://github.com/ansible/team-devtools/tree/main/.agents/skills/architecture-diagram

This tells anyone viewing the diagram on the Miro board where to find
the source for updates or regeneration.

---

## Output Directory

All output goes to `.architecture-diagrams/` in the workspace root:

```text
.architecture-diagrams/
├── dependencies.json           # Crawl results (intermediate)
├── l1_system_context.py        # L1 diagram source
├── l1_system_context.png       # L1 rendered
├── l2_container.py             # L2 diagram source
├── l2_container.png            # L2 rendered
├── l3_component_*.py           # L3 diagram sources (per-repo)
└── l3_component_*.png          # L3 rendered
```

Add `.architecture-diagrams/` to `.gitignore` if not already present.

## Scripts

| File | Purpose |
|------|---------|
| `scripts/arch_models.py` | Data classes, repo manifest, package name mappings |
| `scripts/crawl_repos.py` | Clone + introspect repos, output `dependencies.json` |
| `scripts/generate_diagram.py` | Consume crawl data, produce C4 diagram `.py` files |
| `scripts/render.py` | Render diagram `.py` files to PNG via `c4 export` |
