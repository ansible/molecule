"""Data models for ADT architecture diagram generation.

Defines the repo manifest, component metadata, and relationship types
used by the crawler and diagram generator.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path


class RepoTier(str, Enum):
    """Repository tier classification.

    Attributes:
        PRIMARY: Primary tier repositories.
        EXPERIMENTAL: Experimental repositories.
        COMMUNITY: Community-maintained repositories.
        CONTAINER: Container image repositories.
        AI_PLATFORM: AI platform repositories.
        ADJACENT: Adjacent ecosystem repositories.
        EXTERNAL: External third-party repositories.

    """

    PRIMARY = "primary"
    EXPERIMENTAL = "experimental"
    COMMUNITY = "community"
    CONTAINER = "container"
    AI_PLATFORM = "ai_platform"
    ADJACENT = "adjacent"
    EXTERNAL = "external"


class RepoLanguage(str, Enum):
    """Primary language of a repository.

    Attributes:
        PYTHON: Python language.
        TYPESCRIPT: TypeScript language.
        MIXED: Multiple languages.
        YAML: YAML-only content.

    """

    PYTHON = "Python"
    TYPESCRIPT = "TypeScript"
    MIXED = "Mixed"
    YAML = "YAML"


class RelationshipType(str, Enum):
    """Type of dependency relationship between components.

    Attributes:
        DEPENDS: Direct dependency relationship.
        SPAWNS: Spawns a CLI subprocess.
        PACKAGES: Packages into container image.
        CONSUMES_API: Consumes a remote API.
        EXTENDS: Extends or inherits from.
        TESTS_WITH: Uses for testing.
        BUILDS: Builds an artifact.
        OPTIONAL: Optional soft dependency.
        CONTAINS: Contains as sub-component.
        ESCALATES_TO: Escalates processing to.
        USES_WORKFLOW: Uses a reusable workflow.

    """

    DEPENDS = "depends on"
    SPAWNS = "spawns CLI"
    PACKAGES = "packages into image"
    CONSUMES_API = "consumes API"
    EXTENDS = "extends"
    TESTS_WITH = "tests with"
    BUILDS = "builds"
    OPTIONAL = "optional dependency"
    CONTAINS = "contains"
    ESCALATES_TO = "escalates to"
    USES_WORKFLOW = "uses reusable workflow"


@dataclass
class RepoManifestEntry:
    """A repository to clone and introspect.

    Attributes:
        slug: GitHub org/repo identifier.
        clone_url: URL for cloning the repo.
        language: Primary programming language.
        tier: Repository tier classification.
        description: Short repo description.
        special_handling: Custom crawl logic key.

    """

    slug: str
    clone_url: str
    language: RepoLanguage
    tier: RepoTier
    description: str
    special_handling: str = ""


@dataclass
class DiscoveredComponent:
    """A component discovered inside a repository.

    Attributes:
        name: Component display name.
        repo_slug: Owning repository slug.
        component_type: Kind of component.
        technology: Primary technology used.
        description: Short component description.

    """

    name: str
    repo_slug: str
    component_type: str  # "library", "cli", "server", "extension", "container", "frontend", "proxy"
    technology: str
    description: str


@dataclass
class DiscoveredRelationship:
    """A dependency relationship discovered between components.

    Attributes:
        source: Source repo or component name.
        target: Target repo or component name.
        relationship_type: Kind of relationship.
        label: Human-readable edge label.
        discovered_from: File path where found.

    """

    source: str  # repo slug or component name
    target: str  # repo slug or component name
    relationship_type: RelationshipType
    label: str
    discovered_from: str  # file path where this was found


@dataclass
class ContainerArtifact:
    """A container image built by a repo.

    Attributes:
        repo_slug: Owning repository slug.
        image_name: Published container image name.
        containerfile_path: Path to Containerfile.
        base_image: Base image reference.
        contents: Packages installed in image.
        published_in_workflow: CI workflow that builds it.

    """

    repo_slug: str
    image_name: str
    containerfile_path: str
    base_image: str
    contents: list[str] = field(default_factory=list)
    published_in_workflow: str = ""


@dataclass
class CrawlResult:
    """Aggregated output from crawling all repos.

    Attributes:
        repos: Map of slug to manifest entry.
        components: Discovered components list.
        relationships: Discovered relationships list.
        containers: Container artifacts found.
        crawl_errors: Errors encountered during crawl.

    """

    repos: dict[str, RepoManifestEntry] = field(default_factory=dict)
    components: list[DiscoveredComponent] = field(default_factory=list)
    relationships: list[DiscoveredRelationship] = field(default_factory=list)
    containers: list[ContainerArtifact] = field(default_factory=list)
    crawl_errors: list[str] = field(default_factory=list)

    def to_json(self, path: Path) -> None:
        """Serialize to JSON for agent review.

        Args:
            path: Output file path.

        """

        def _default(o: object) -> object:
            if isinstance(o, Enum):
                return o.value
            if isinstance(o, Path):
                return str(o)
            msg = f"Object of type {type(o)} is not JSON serializable"
            raise TypeError(msg)

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(asdict(self), f, indent=2, default=_default)

    @classmethod
    def from_json(cls, path: Path) -> CrawlResult:
        """Deserialize from JSON.

        Args:
            path: Input JSON file path.

        Returns:
            Deserialized crawl result.

        """
        with path.open() as f:
            data = json.load(f)
        result = cls()
        for slug, entry in data.get("repos", {}).items():
            entry["language"] = RepoLanguage(entry["language"])
            entry["tier"] = RepoTier(entry["tier"])
            result.repos[slug] = RepoManifestEntry(**entry)
        for comp in data.get("components", []):
            result.components.append(DiscoveredComponent(**comp))
        for rel in data.get("relationships", []):
            rel["relationship_type"] = RelationshipType(rel["relationship_type"])
            result.relationships.append(DiscoveredRelationship(**rel))
        for ctr in data.get("containers", []):
            result.containers.append(ContainerArtifact(**ctr))
        result.crawl_errors = data.get("crawl_errors", [])
        return result


# ---------------------------------------------------------------------------
# Repo manifest -- the canonical list of repos to clone and introspect.
# ---------------------------------------------------------------------------

REPO_MANIFEST: list[RepoManifestEntry] = [
    # --- ADT Primary ---
    RepoManifestEntry(
        slug="ansible/ansible-dev-tools",
        clone_url="https://github.com/ansible/ansible-dev-tools",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Meta-package + container image builds (ADT bundle)",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-lint",
        clone_url="https://github.com/ansible/ansible-lint",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Playbook/role/collection linter",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-compat",
        clone_url="https://github.com/ansible/ansible-compat",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Shared compatibility/testing library",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-navigator",
        clone_url="https://github.com/ansible/ansible-navigator",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="TUI for execution environments",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-dev-environment",
        clone_url="https://github.com/ansible/ansible-dev-environment",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Virtual environment manager (ade)",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-creator",
        clone_url="https://github.com/ansible/ansible-creator",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Scaffolding tool for Ansible content",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-sign",
        clone_url="https://github.com/ansible/ansible-sign",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Content signing",
    ),
    RepoManifestEntry(
        slug="ansible/molecule",
        clone_url="https://github.com/ansible/molecule",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Functional test runner for Ansible roles",
    ),
    RepoManifestEntry(
        slug="ansible/vscode-ansible",
        clone_url="https://github.com/ansible/vscode-ansible",
        language=RepoLanguage.TYPESCRIPT,
        tier=RepoTier.PRIMARY,
        description="VS Code extension with language server + MCP server",
        special_handling="vscode",
    ),
    RepoManifestEntry(
        slug="ansible/team-devtools",
        clone_url="https://github.com/ansible/team-devtools",
        language=RepoLanguage.MIXED,
        tier=RepoTier.PRIMARY,
        description="Meta-repo: shared CI, skills, config, practices",
    ),
    # --- ADT Experimental / Testing / Community ---
    RepoManifestEntry(
        slug="ansible/pytest-ansible",
        clone_url="https://github.com/ansible/pytest-ansible",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Pytest plugin for Ansible",
    ),
    RepoManifestEntry(
        slug="ansible/tox-ansible",
        clone_url="https://github.com/ansible/tox-ansible",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.PRIMARY,
        description="Tox plugin for Ansible",
    ),
    RepoManifestEntry(
        slug="ansible/actions",
        clone_url="https://github.com/ansible/actions",
        language=RepoLanguage.YAML,
        tier=RepoTier.EXPERIMENTAL,
        description="Shared GitHub Actions",
    ),
    RepoManifestEntry(
        slug="ansible/ansible-content-actions",
        clone_url="https://github.com/ansible/ansible-content-actions",
        language=RepoLanguage.YAML,
        tier=RepoTier.EXPERIMENTAL,
        description="Marketplace GitHub Actions for content",
    ),
    RepoManifestEntry(
        slug="ansible/mkdocs-ansible",
        clone_url="https://github.com/ansible/mkdocs-ansible",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.COMMUNITY,
        description="MkDocs theme for Ansible docs",
    ),
    # --- AAP Container Repos ---
    RepoManifestEntry(
        slug="ansible-automation-platform/ansible-devtools-container",
        clone_url="https://github.com/ansible-automation-platform/ansible-devtools-container",
        language=RepoLanguage.MIXED,
        tier=RepoTier.CONTAINER,
        description="Downstream devtools container -- packages ADT web server",
    ),
    RepoManifestEntry(
        slug="ansible-automation-platform/ansible-devspaces-container",
        clone_url="https://github.com/ansible-automation-platform/ansible-devspaces-container",
        language=RepoLanguage.MIXED,
        tier=RepoTier.CONTAINER,
        description="Downstream devspaces container",
    ),
    # --- Abbenay (AI Daemon) ---
    RepoManifestEntry(
        slug="redhat-developer/abbenay",
        clone_url="https://github.com/redhat-developer/abbenay",
        language=RepoLanguage.TYPESCRIPT,
        tier=RepoTier.AI_PLATFORM,
        description="Unified AI daemon and library for LLM providers",
        special_handling="abbenay",
    ),
    # --- APME (External Consumer) ---
    RepoManifestEntry(
        slug="ansible/apme",
        clone_url="https://github.com/ansible/apme",
        language=RepoLanguage.PYTHON,
        tier=RepoTier.ADJACENT,
        description="Ansible policy and management engine; depends on Abbenay for AI remediation",
    ),
]

# Known ADT package names for dependency matching.
# Maps pip/npm package names to repo slugs.
ADT_PACKAGE_MAP: dict[str, str] = {
    # Python packages
    "ansible-compat": "ansible/ansible-compat",
    "ansible-creator": "ansible/ansible-creator",
    "ansible-dev-environment": "ansible/ansible-dev-environment",
    "ansible-dev-tools": "ansible/ansible-dev-tools",
    "ansible-lint": "ansible/ansible-lint",
    "ansible-navigator": "ansible/ansible-navigator",
    "ansible-sign": "ansible/ansible-sign",
    "molecule": "ansible/molecule",
    "pytest-ansible": "ansible/pytest-ansible",
    "tox-ansible": "ansible/tox-ansible",
    "mkdocs-ansible": "ansible/mkdocs-ansible",
    "subprocess-tee": "pycontribs/subprocess-tee",
    "ansible-builder": "ansible/ansible-builder",
    "ansible-runner": "ansible/ansible-runner",
    "apme-engine": "ansible/apme",
    # npm packages
    "abbenay-client": "redhat-developer/abbenay",
    "abbenay_grpc": "redhat-developer/abbenay",
    "@abbenay/core": "redhat-developer/abbenay",
    "@abbenay/daemon": "redhat-developer/abbenay",
}

# Python CLI tool names that vscode-ansible may spawn.
PYTHON_CLI_TOOLS: dict[str, str] = {
    "ansible-lint": "ansible/ansible-lint",
    "ansible-navigator": "ansible/ansible-navigator",
    "ansible-creator": "ansible/ansible-creator",
    "ade": "ansible/ansible-dev-environment",
    "ansible-dev-environment": "ansible/ansible-dev-environment",
    "molecule": "ansible/molecule",
    "ansible-sign": "ansible/ansible-sign",
    "ansible-builder": "ansible/ansible-builder",
    "ansible-runner": "ansible/ansible-runner",
    "ansible-playbook": "ansible/ansible-core",
    "ansible-galaxy": "ansible/ansible-core",
    "ansible-config": "ansible/ansible-core",
    "ansible-inventory": "ansible/ansible-core",
    "ansible-vault": "ansible/ansible-core",
}
