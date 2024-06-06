"""Molecule Application Module."""

from ansible_compat.runtime import Runtime


class App:
    """App class that keep runtime status."""

    def __init__(self) -> None:  # noqa: ANN101
        """Create a new app instance."""
        self.runtime = Runtime(isolated=False)


app = App()
