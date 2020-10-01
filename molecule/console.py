"""Console and terminal utils."""

import rich
from rich.console import Console

# , ConsoleOptions, RenderResult
# from rich.markdown import CodeBlock, Markdown
# from rich.syntax import Syntax
from rich.terminal_theme import TerminalTheme
from rich.theme import Theme

TERMINAL_THEME = TerminalTheme(
    (13, 21, 27),
    (220, 220, 220),
    [
        (60, 68, 77),  # black
        (175, 34, 55),  # red
        (62, 179, 131),  # green
        (255, 147, 0),  # yellow
        (38, 107, 133),  # blue
        (203, 62, 118),  # magenta
        (138, 150, 168),  # cyan
        (220, 220, 220),  # white
    ],
    [  # bright
        (81, 93, 104),  # black
        (189, 37, 61),  # red
        (83, 234, 168),  # green
        (253, 227, 129),  # yellow
        (50, 157, 204),  # blue
        (242, 74, 165),  # magenta
        (175, 2195, 219),  # cyan
        (255, 255, 255),  # white
    ],
)
theme = Theme(
    {
        "normal": "",  # No or minor danger
        "moderate": "yellow",  # Moderate danger
        "considerable": "dark_orange",  # Considerable danger
        "high": "red",  # High danger
        "veryhigh": "dim red",  # Very high danger
        "branch": "magenta",
        "wip": "bold yellow",
    }
)


def bootstrap() -> Console:
    """Initialize rich console."""
    # Markdown.elements["code_block"] = MyCodeBlock
    return Console(
        theme=theme, highlighter=rich.highlighter.ReprHighlighter(), record=True
    )


def has_ansi(msg: str) -> bool:
    """Indicate if received text contains ANSI escapes."""
    return "\u001b" in msg


def chomp(x):
    """Remove trailing newlines from string."""
    if x.endswith("\r\n"):
        return x[:-2]
    if x.endswith("\n") or x.endswith("\r"):
        return x[:-1]
    return x


console = bootstrap()
