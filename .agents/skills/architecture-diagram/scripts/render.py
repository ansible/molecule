"""Render C4 diagram Python files to PNG via `c4 export`.

Usage:
    python3 render.py [--input-dir .architecture-diagrams] [--renderer plantuml|mermaid]

Finds all l*.py diagram files in the input directory and exports each to PNG.
Checks for PlantUML (Java) or Mermaid CLI availability before starting.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _find_plantuml_jar() -> str | None:
    """Look for plantuml.jar in common locations.

    Returns:
        Absolute path to plantuml.jar, or ``None`` if not found.

    """
    candidates = [
        Path.home() / ".local" / "lib" / "plantuml.jar",
        Path("/usr/share/java/plantuml.jar"),
        Path("/usr/local/lib/plantuml.jar"),
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return None


def check_prerequisites(renderer: str) -> bool:
    """Verify that the rendering backend is available.

    Args:
        renderer: Backend name (``plantuml`` or ``mermaid``).

    Returns:
        ``True`` if the backend is usable.

    """
    if renderer == "plantuml":
        if shutil.which("plantuml"):
            print("  PlantUML CLI found.")
            return True
        if shutil.which("java"):
            jar = os.environ.get("PLANTUML_JAR") or _find_plantuml_jar()
            if jar:
                os.environ["PLANTUML_JAR"] = jar
                print(f"  Java found. Using PlantUML JAR: {jar}")
            else:
                print("  Java found. c4-diagrams will use its bundled PlantUML JAR.")
            return True
        print(
            "ERROR: PlantUML rendering requires Java or the plantuml CLI.\n"
            "Install options:\n"
            "  - Fedora/RHEL: sudo dnf install plantuml\n"
            "  - macOS:       brew install plantuml\n"
            "  - Manual:      install Java 11+ (sudo dnf install java-17-openjdk)\n"
            "                 c4-diagrams bundles plantuml.jar internally",
            file=sys.stderr,
        )
        return False
    if renderer == "mermaid":
        if shutil.which("mmdc"):
            print("  Mermaid CLI (mmdc) found.")
            return True
        print(
            "ERROR: Mermaid rendering requires mermaid-cli (mmdc).\nInstall: npm install -g @mermaid-js/mermaid-cli",
            file=sys.stderr,
        )
        return False
    return False


def render_diagram(diagram_py: Path, output_dir: Path, renderer: str) -> Path | None:
    """Run ``c4 export`` on a single diagram file and return the PNG path.

    Args:
        diagram_py: Path to the diagram Python file.
        output_dir: Directory for the rendered PNG output.
        renderer: Backend name (``plantuml`` or ``mermaid``).

    Returns:
        Path to the rendered PNG, or ``None`` on failure.

    """
    png_path = output_dir / (diagram_py.stem + ".png")

    cmd = ["c4", "export"]
    if renderer == "mermaid":
        cmd.extend(["--renderer", "mermaid"])
    cmd.append(str(diagram_py))

    env = os.environ.copy()
    env["PLANTUML_LIMIT_SIZE"] = "16384"

    print(f"  Rendering {diagram_py.name} -> {png_path.name} ...", end=" ", flush=True)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=120,
            env=env,
            check=False,
        )
    except FileNotFoundError:
        print("FAILED (c4 command not found -- is c4-diagrams installed?)")
        return None
    except subprocess.TimeoutExpired:
        print("FAILED (timeout after 120s)")
        return None
    else:
        if proc.returncode != 0:
            stderr = proc.stderr.decode(errors="replace")
            print(f"FAILED\n    {stderr[:500]}")
            return None

        png_path.write_bytes(proc.stdout)
        size_kb = len(proc.stdout) / 1024
        print(f"OK ({size_kb:.0f} KB)")
        return png_path


def main() -> None:
    """Render C4 diagram files to PNG via CLI."""
    parser = argparse.ArgumentParser(description="Render C4 diagram .py files to PNG")
    parser.add_argument(
        "--input-dir",
        default=".architecture-diagrams",
        help="Directory containing diagram .py files",
    )
    parser.add_argument(
        "--renderer",
        choices=["plantuml", "mermaid"],
        default="plantuml",
        help="Rendering backend",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"ERROR: {input_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Checking prerequisites for {args.renderer} renderer ...")
    if not check_prerequisites(args.renderer):
        sys.exit(1)

    diagram_files = sorted(input_dir.glob("l*.py"))
    if not diagram_files:
        print(f"No diagram files (l*.py) found in {input_dir}")
        sys.exit(1)

    print(f"\nRendering {len(diagram_files)} diagram(s) ...")
    rendered: list[Path] = []
    failed: list[str] = []
    for df in diagram_files:
        png = render_diagram(df, input_dir, args.renderer)
        if png:
            rendered.append(png)
        else:
            failed.append(df.name)

    print("\nResults:")
    print(f"  {len(rendered)} rendered successfully")
    if failed:
        print(f"  {len(failed)} failed: {', '.join(failed)}")

    if rendered:
        print(f"\nPNG files in {input_dir}/:")
        for p in rendered:
            print(f"  {p}")


if __name__ == "__main__":
    main()
