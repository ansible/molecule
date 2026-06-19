"""Clone and introspect ADT ecosystem repos to discover dependencies.

Usage:
    python3 crawl_repos.py [--clone-dir /tmp/adt-c4-repos] [--output dependencies.json]

Clones every repo in the manifest (shallow, default branch) and reads
actual dependency files to build the real relationship graph.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from arch_models import (  # pylint: disable=import-error
        ADT_PACKAGE_MAP,
        PYTHON_CLI_TOOLS,
        REPO_MANIFEST,
        ContainerArtifact,
        CrawlResult,
        DiscoveredComponent,
        DiscoveredRelationship,
        RelationshipType,
        RepoLanguage,
        RepoManifestEntry,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from arch_models import (
        ADT_PACKAGE_MAP,
        PYTHON_CLI_TOOLS,
        REPO_MANIFEST,
        ContainerArtifact,
        CrawlResult,
        DiscoveredComponent,
        DiscoveredRelationship,
        RelationshipType,
        RepoLanguage,
        RepoManifestEntry,
    )

# ---------------------------------------------------------------------------
# Cloning
# ---------------------------------------------------------------------------


def clone_all(clone_dir: Path) -> dict[str, Path]:
    """Shallow-clone every manifest repo into *clone_dir*.

    Skips repos that fail to clone (prints a warning).

    Args:
        clone_dir: Directory to clone repos into (will be recreated).

    Returns:
        Mapping of repo slug to local clone path.

    """
    if clone_dir.exists():
        shutil.rmtree(clone_dir)
    clone_dir.mkdir(parents=True)

    cloned: dict[str, Path] = {}
    for entry in REPO_MANIFEST:
        dest = clone_dir / entry.slug.replace("/", "__")
        print(f"  Cloning {entry.slug} ...", flush=True)
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--quiet", entry.clone_url, str(dest)],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            cloned[entry.slug] = dest
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            print(f"  WARNING: failed to clone {entry.slug}: {exc}", file=sys.stderr)
    return cloned


# ---------------------------------------------------------------------------
# Introspection helpers
# ---------------------------------------------------------------------------


def _read_toml_deps(pyproject: Path) -> list[str]:
    """Extract dependency names from pyproject.toml without a TOML library.

    Args:
        pyproject: Path to pyproject.toml file.

    Returns:
        Lowercased dependency package names.

    """
    text = pyproject.read_text(encoding="utf-8")
    deps: list[str] = []
    in_deps = False
    in_optional = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "[project.dependencies]" or stripped.startswith(
            "dependencies = [",
        ):
            in_deps = True
            continue
        if re.match(r"\[project\.optional-dependencies\.", stripped):
            in_optional = True
            continue
        if stripped.startswith("[") and not stripped.startswith(
            "[project.optional-dependencies",
        ):
            in_deps = False
            in_optional = False
            continue
        if in_deps or in_optional:
            m = re.match(r'["\']([a-zA-Z0-9_-]+)', stripped)
            if m:
                deps.append(m.group(1).lower())
    return deps


def _read_package_json_deps(pkg_json: Path) -> list[str]:
    """Extract dependency names from package.json.

    Args:
        pkg_json: Path to package.json file.

    Returns:
        Dependency package names.

    """
    try:
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    names: list[str] = []
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        names.extend(data.get(section, {}).keys())
    return names


def _find_containerfiles(repo_dir: Path) -> list[Path]:
    """Find Containerfile / Dockerfile variants.

    Args:
        repo_dir: Root directory of the cloned repository.

    Returns:
        Paths to discovered container definition files.

    """
    candidates = ["Containerfile", "Dockerfile"]
    found: list[Path] = [p for name in candidates for p in repo_dir.rglob(name)]
    found.extend(repo_dir.rglob("*.containerfile"))
    found.extend(repo_dir.rglob("*.dockerfile"))
    return found


def _parse_containerfile(
    cf: Path,
    repo_slug: str,
    repo_dir: Path,
) -> ContainerArtifact | None:
    """Extract base image and notable contents from a Containerfile.

    Args:
        cf: Path to the Containerfile.
        repo_slug: Repository slug (e.g. ``ansible/ansible-lint``).
        repo_dir: Root directory of the cloned repository.

    Returns:
        Parsed container artifact, or ``None`` if unparsable.

    """
    try:
        text = cf.read_text(encoding="utf-8")
    except OSError:
        return None
    base_image = ""
    contents: list[str] = []
    image_label = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("FROM ") and not base_image:
            base_image = stripped.split()[1] if len(stripped.split()) > 1 else ""
        if "pip install" in stripped or "pip3 install" in stripped:
            contents.append(stripped)
        if "COPY" in stripped.upper() or "ADD" in stripped.upper():
            contents.append(stripped)
        label_m = re.search(r'org\.opencontainers\.image\.title[="]([^"]+)', stripped)
        if label_m:
            image_label = label_m.group(1).strip()
    if not base_image:
        return None

    # Determine image name: prefer OCI label, then derive from path
    if image_label:
        image_name = image_label
    else:
        parent_dir = cf.parent.name if cf.parent != repo_dir else ""
        if parent_dir:
            image_name = f"{repo_slug.rsplit('/', maxsplit=1)[-1]}-{parent_dir}"
        else:
            image_name = repo_slug.rsplit("/", maxsplit=1)[-1]

    return ContainerArtifact(
        repo_slug=repo_slug,
        image_name=image_name,
        containerfile_path=str(cf.relative_to(repo_dir)),
        base_image=base_image,
        contents=contents[:20],
    )


def _scan_workflow_container_builds(
    repo_dir: Path,
    repo_slug: str,
) -> list[ContainerArtifact]:
    """Scan GitHub Actions workflows and build scripts for container image builds/pushes.

    Args:
        repo_dir: Root directory of the cloned repository.
        repo_slug: Repository slug.

    Returns:
        Container artifacts found in workflows.

    """
    artifacts: list[ContainerArtifact] = []
    seen_images: set[str] = set()

    # Scan workflow YAML files
    scan_files: list[tuple[Path, str]] = []
    wf_dir = repo_dir / ".github" / "workflows"
    if wf_dir.is_dir():
        scan_files.extend((yml, yml.name) for yml in wf_dir.glob("*.yml"))

    # Also scan shell scripts in tools/ that often contain image publishing
    tools_dir = repo_dir / "tools"
    if tools_dir.is_dir():
        scan_files.extend((sh, f"tools/{sh.name}") for sh in tools_dir.glob("*.sh"))

    for scan_path, source_label in scan_files:
        try:
            text = scan_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(
            kw in text
            for kw in [
                "docker/build-push-action",
                "buildah",
                "podman build",
                "docker build",
                "ghcr.io",
                "quay.io",
            ]
        ):
            image_refs = re.findall(r"(?:ghcr\.io|quay\.io)/[\w./-]+", text)
            for ref in image_refs:
                base = re.sub(r"[:@].*", "", ref)
                base = re.sub(r"-tmp$", "", base)
                if base not in seen_images:
                    seen_images.add(base)
                    artifacts.append(
                        ContainerArtifact(
                            repo_slug=repo_slug,
                            image_name=base,
                            containerfile_path="(workflow/script)",
                            base_image="(from workflow)",
                            published_in_workflow=source_label,
                        ),
                    )

    return artifacts


def _scan_workflow_reusable(
    repo_dir: Path,
    repo_slug: str,
) -> list[DiscoveredRelationship]:
    """Discover reusable workflow references to other ADT repos.

    Args:
        repo_dir: Root directory of the cloned repository.
        repo_slug: Repository slug.

    Returns:
        Relationships for reusable workflow references.

    """
    rels: list[DiscoveredRelationship] = []
    wf_dir = repo_dir / ".github" / "workflows"
    if not wf_dir.is_dir():
        return rels
    for yml in wf_dir.glob("*.yml"):
        try:
            text = yml.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in re.finditer(r"uses:\s+([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)/", text):
            target = m.group(1)
            if target != repo_slug and any(target == e.slug for e in REPO_MANIFEST):
                rels.append(
                    DiscoveredRelationship(
                        source=repo_slug,
                        target=target,
                        relationship_type=RelationshipType.USES_WORKFLOW,
                        label="uses reusable workflow",
                        discovered_from=yml.name,
                    ),
                )
    return rels


# ---------------------------------------------------------------------------
# Special-case crawlers
# ---------------------------------------------------------------------------


def _crawl_vscode_ansible(repo_dir: Path, result: CrawlResult) -> None:  # noqa: PLR0912
    """Deep crawl vscode-ansible for language server, MCP, and Python CLI spawns.

    Args:
        repo_dir: Root directory of the cloned repository.
        result: Accumulator for discovered components and relationships.

    """
    slug = "ansible/vscode-ansible"

    # Scan extension source (src/) for Python CLI tool references
    src_dir = repo_dir / "src"
    if not src_dir.is_dir():
        src_dir = repo_dir
    for ext in ("*.ts", "*.js", "*.json"):
        for f in src_dir.rglob(ext):
            try:
                text = f.read_text(errors="ignore")
            except OSError:
                continue
            for tool_name, tool_slug in PYTHON_CLI_TOOLS.items():
                if tool_name in text and tool_slug != slug:
                    result.relationships.append(
                        DiscoveredRelationship(
                            source=slug,
                            target=tool_slug,
                            relationship_type=RelationshipType.SPAWNS,
                            label=f"spawns {tool_name}",
                            discovered_from=str(f.relative_to(repo_dir)),
                        ),
                    )

    # Detect language server
    for f in src_dir.rglob("*.ts"):
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        if "LanguageClient" in text or "createConnection" in text or "LanguageServer" in text:
            result.components.append(
                DiscoveredComponent(
                    name="Ansible Language Server",
                    repo_slug=slug,
                    component_type="server",
                    technology="TypeScript (LSP)",
                    description="Integrated language server for Ansible content editing",
                ),
            )
            break

    # Detect and crawl MCP server package
    mcp_dir = repo_dir / "packages" / "ansible-mcp-server"
    mcp_found = False
    if mcp_dir.is_dir():
        mcp_found = True
        result.components.append(
            DiscoveredComponent(
                name="Ansible MCP Server",
                repo_slug=slug,
                component_type="server",
                technology="TypeScript (MCP)",
                description="Model Context Protocol server exposing ADT CLI tools to AI agents",
            ),
        )
        # Scan MCP server source for Python CLI tool dependencies
        mcp_src = mcp_dir / "src"
        if mcp_src.is_dir():
            for f in mcp_src.rglob("*.ts"):
                try:
                    text = f.read_text(errors="ignore")
                except OSError:
                    continue
                for tool_name, tool_slug in PYTHON_CLI_TOOLS.items():
                    if tool_name in text and tool_slug != slug:
                        result.relationships.append(
                            DiscoveredRelationship(
                                source="Ansible MCP Server",
                                target=tool_slug,
                                relationship_type=RelationshipType.SPAWNS,
                                label=f"MCP tool: {tool_name}",
                                discovered_from=f"packages/ansible-mcp-server/src/{f.relative_to(mcp_src)}",
                            ),
                        )

    if not mcp_found:
        # Fallback: detect MCP from extension source
        for f in src_dir.rglob("*.ts"):
            try:
                text = f.read_text(errors="ignore")
            except OSError:
                continue
            if "mcp" in text.lower() and ("server" in text.lower() or "McpServer" in text or "MCP" in text):
                result.components.append(
                    DiscoveredComponent(
                        name="Ansible MCP Server",
                        repo_slug=slug,
                        component_type="server",
                        technology="TypeScript (MCP)",
                        description="Model Context Protocol server for AI tool integration",
                    ),
                )
                break


def _crawl_abbenay(repo_dir: Path, result: CrawlResult) -> None:
    """Crawl abbenay monorepo for sub-packages and Containerfile.

    Args:
        repo_dir: Root directory of the cloned repository.
        result: Accumulator for discovered components and relationships.

    """
    slug = "redhat-developer/abbenay"
    packages_dir = repo_dir / "packages"
    if packages_dir.is_dir():
        for pkg in packages_dir.iterdir():
            if not pkg.is_dir():
                continue
            pkg_json = pkg / "package.json"
            desc = ""
            tech = "TypeScript"
            ctype = "library"
            if pkg_json.exists():
                try:
                    data = json.loads(pkg_json.read_text(encoding="utf-8"))
                    desc = data.get("description", "")
                except (json.JSONDecodeError, OSError):
                    pass
            name = pkg.name
            if name == "daemon":
                ctype = "server"
                desc = desc or "gRPC server, web dashboard, CLI, VS Code backchannel"
            elif name == "core":
                ctype = "library"
                desc = desc or "LLM engine abstraction, streaming chat, model discovery"
            elif name == "vscode":
                ctype = "extension"
                desc = desc or "VS Code extension for Abbenay"
            elif name == "python":
                ctype = "library"
                tech = "Python"
                desc = desc or "Python gRPC client"
            elif name == "proto-ts":
                ctype = "library"
                desc = desc or "Generated TypeScript proto stubs"
            result.components.append(
                DiscoveredComponent(
                    name=f"@abbenay/{name}" if name != "python" else "abbenay-python-client",
                    repo_slug=slug,
                    component_type=ctype,
                    technology=tech,
                    description=desc,
                ),
            )


# ---------------------------------------------------------------------------
# Generic crawler
# ---------------------------------------------------------------------------


def crawl_repo(entry: RepoManifestEntry, repo_dir: Path, result: CrawlResult) -> None:  # noqa: PLR0912
    """Introspect a single cloned repo and add findings to *result*.

    Args:
        entry: Manifest entry for the repository.
        repo_dir: Root directory of the cloned repository.
        result: Accumulator for discovered components and relationships.

    """
    slug = entry.slug

    # --- Python dependencies ---
    pyproject = repo_dir / "pyproject.toml"
    if pyproject.exists():
        for dep_name in _read_toml_deps(pyproject):
            target_slug = ADT_PACKAGE_MAP.get(dep_name)
            if target_slug and target_slug != slug:
                result.relationships.append(
                    DiscoveredRelationship(
                        source=slug,
                        target=target_slug,
                        relationship_type=RelationshipType.DEPENDS,
                        label=f"depends on {dep_name}",
                        discovered_from="pyproject.toml",
                    ),
                )

    # --- Node dependencies ---
    pkg_json = repo_dir / "package.json"
    if pkg_json.exists():
        for dep_name in _read_package_json_deps(pkg_json):
            target_slug = ADT_PACKAGE_MAP.get(dep_name)
            if target_slug and target_slug != slug:
                result.relationships.append(
                    DiscoveredRelationship(
                        source=slug,
                        target=target_slug,
                        relationship_type=RelationshipType.DEPENDS,
                        label=f"depends on {dep_name}",
                        discovered_from="package.json",
                    ),
                )

    # --- Python source: CLI tool spawns (catches runtime deps not in pyproject.toml) ---
    if entry.language in (RepoLanguage.PYTHON, RepoLanguage.MIXED):
        for f in repo_dir.rglob("*.py"):
            if ".tox" in str(f) or "venv" in str(f) or "__pycache__" in str(f):
                continue
            try:
                text = f.read_text(errors="ignore")
            except OSError:
                continue
            for tool_name, tool_slug in PYTHON_CLI_TOOLS.items():
                if tool_slug == slug:
                    continue
                if re.search(rf'["\'](?:echo\s.*)?{re.escape(tool_name)}\b', text):
                    result.relationships.append(
                        DiscoveredRelationship(
                            source=slug,
                            target=tool_slug,
                            relationship_type=RelationshipType.SPAWNS,
                            label=f"spawns {tool_name}",
                            discovered_from=str(f.relative_to(repo_dir)),
                        ),
                    )

    # --- Container artifacts (merge Containerfile builds with workflow registry names) ---
    cf_artifacts = []
    for cf in _find_containerfiles(repo_dir):
        artifact = _parse_containerfile(cf, slug, repo_dir)
        if artifact:
            cf_artifacts.append(artifact)

    wf_artifacts = _scan_workflow_container_builds(repo_dir, slug)

    # Match workflow registry names to Containerfile builds by shared keywords
    matched_wf: set[int] = set()
    matched_cf: set[int] = set()
    for i, wf in enumerate(wf_artifacts):
        wf_key = wf.image_name.split("/")[-1].lower()
        for j, cf in enumerate(cf_artifacts):
            if j in matched_cf:
                continue
            cf_key = cf.image_name.lower()
            cf_suffix = cf_key.split("-")[-1]
            # Match by: shared substring or Containerfile directory name in registry name
            if wf_key in cf_key or cf_suffix in wf_key or cf_key in wf_key:
                cf.image_name = wf.image_name
                cf.published_in_workflow = wf.published_in_workflow
                matched_wf.add(i)
                matched_cf.add(j)
                break

    # Any unmatched Containerfile whose directory is generic (e.g. "final") gets
    # paired with the first unmatched workflow artifact from the same repo
    unmatched_cf = [j for j in range(len(cf_artifacts)) if j not in matched_cf]
    unmatched_wf = [i for i in range(len(wf_artifacts)) if i not in matched_wf]
    for j, i in zip(unmatched_cf, unmatched_wf, strict=False):
        cf_artifacts[j].image_name = wf_artifacts[i].image_name
        cf_artifacts[j].published_in_workflow = wf_artifacts[i].published_in_workflow
        matched_wf.add(i)

    result.containers.extend(cf_artifacts)
    for i, wf in enumerate(wf_artifacts):
        if i not in matched_wf:
            result.containers.extend([wf])

    # --- Reusable workflow references ---
    result.relationships.extend(_scan_workflow_reusable(repo_dir, slug))

    # --- Special handling ---
    if entry.special_handling == "vscode":
        _crawl_vscode_ansible(repo_dir, result)
    elif entry.special_handling == "abbenay":
        _crawl_abbenay(repo_dir, result)


def deduplicate_relationships(
    rels: list[DiscoveredRelationship],
) -> list[DiscoveredRelationship]:
    """Remove duplicate relationships (same source, target, type).

    Args:
        rels: Relationships to deduplicate.

    Returns:
        Unique relationships.

    """
    seen: set[tuple[str, str, str]] = set()
    unique: list[DiscoveredRelationship] = []
    for r in rels:
        key = (r.source, r.target, r.relationship_type.value)
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Clone and crawl ADT repos for C4 diagram generation."""
    parser = argparse.ArgumentParser(
        description="Clone and crawl ADT repos for C4 diagrams",
    )
    parser.add_argument(
        "--clone-dir",
        default="/tmp/adt-c4-repos",  # noqa: S108
        help="Directory for shallow clones",
    )
    parser.add_argument(
        "--output",
        default=".architecture-diagrams/dependencies.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    clone_dir = Path(args.clone_dir)
    output_path = Path(args.output)

    print(f"Cloning {len(REPO_MANIFEST)} repos into {clone_dir} ...")
    cloned = clone_all(clone_dir)
    print(f"Successfully cloned {len(cloned)}/{len(REPO_MANIFEST)} repos.\n")

    result = CrawlResult()
    for entry in REPO_MANIFEST:
        result.repos[entry.slug] = entry
        repo_dir = cloned.get(entry.slug)
        if repo_dir is None:
            result.crawl_errors.append(f"Failed to clone {entry.slug}")
            continue
        print(f"  Crawling {entry.slug} ...")
        try:
            crawl_repo(entry, repo_dir, result)
        except Exception as exc:  # noqa: BLE001
            msg = f"Error crawling {entry.slug}: {exc}"
            print(f"  WARNING: {msg}", file=sys.stderr)
            result.crawl_errors.append(msg)

    result.relationships = deduplicate_relationships(result.relationships)

    print("\nDiscovered:")
    print(f"  {len(result.components)} components")
    print(f"  {len(result.relationships)} relationships")
    print(f"  {len(result.containers)} container artifacts")
    if result.crawl_errors:
        print(f"  {len(result.crawl_errors)} errors")

    result.to_json(output_path)
    print(f"\nOutput written to {output_path}")


if __name__ == "__main__":
    main()
