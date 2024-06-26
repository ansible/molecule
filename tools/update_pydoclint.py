"""Update the flake exception list."""

import configparser
import re
import subprocess

from pathlib import Path


def main() -> None:
    """Update the flake exception list.

    Raises:
        ValueError: If the output of flake8 is not as expected.
    """
    result = subprocess.run(
        "flake8 --per-file-ignores=foo:NULL",  # noqa: S607
        shell=True,  # noqa: S602
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).parent.parent,
    )
    entries: dict[str, set[str]] = {}
    for line in result.stdout.splitlines():
        match = re.match(r"^\./(?P<file>.*?):.*(?P<code>DOC\d+)", line)
        if not match:
            err = "Failed to parse: {line}"
            raise ValueError(err)
        match_dict = match.groupdict()
        entries.setdefault(match_dict["file"], set())
        entries[match_dict["file"]].add(match_dict["code"])
    flake8 = Path(__file__).parent.parent / ".flake8"
    parser = configparser.ConfigParser()
    parser.read(flake8)
    lines = []
    for file, codes in entries.items():
        lines.append(f"{file}: {','.join(sorted(codes))}")
    parser["flake8"]["per-file-ignores"] = "\n" + "\n".join(lines)
    with flake8.open("w") as f:
        parser.write(f)


if __name__ == "__main__":
    main()
