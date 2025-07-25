"""Location to define Molecule report formats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molecule.ansi_output import AnsiOutput
from molecule.util import safe_dump


if TYPE_CHECKING:
    from molecule.types import ScenariosResults


def table(results: list[ScenariosResults]) -> str:
    """Print end-of-run report as a table.

    Args:
        results: Dictionary containing results from each scenario.

    Returns:
        The formatted end-of-run report.
    """
    scenario_width = 0
    action_width = 0
    parts = []
    for scenario in results:
        scenario_width = max(scenario_width, len(scenario["name"]))
        for result in scenario["results"]:
            action_width = max(action_width, len(result["subcommand"]))
            parts.append([scenario["name"], result["subcommand"], result["state"]])

    rows = []
    ansi = AnsiOutput()
    scenario_name = ""
    for name, subcommand, state in parts:
        if name != scenario_name:
            string = f"{name.ljust(scenario_width)} {subcommand.ljust(action_width)} "
            scenario_name = name
        else:
            string = f"{''.ljust(scenario_width)} {subcommand.ljust(action_width)} "
        match state:
            case "PASSED":
                string += f"[GREEN]{state}[/]"
            case "SKIPPED":
                string += f"[CYAN]{state}[/]"
            case "FAILED":
                string += f"[RED]{state}[/]"
            case _:
                string += state
        rows.append(ansi.process_markup(string))

    return "\n".join(rows)


def yaml(results: list[ScenariosResults]) -> str:
    """Print end-of-run report.

    Args:
        results: Dictionary containing results from each scenario.

    Returns:
        The formatted end-of-run report.
    """
    return safe_dump(results)


FORMATS = {
    "table": table,
    "yaml": yaml,
}
