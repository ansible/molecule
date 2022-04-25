"""cookiecutter main function."""
import os
import sys
from copy import copy

from molecule.generate import generate_context, generate_files


def cookiecutter(
    template,
    extra_context=None,
    output_dir=".",
):
    """
    Run Cookiecutter just as if using it from the command line.

    :param template: A directory containing a project template directory,
        or a URL to a git repository.
    :param no_input: Prompt the user at command line for manual configuration?
    :param extra_context: A dictionary of context that overrides default
        and user configuration.
    :param output_dir: Where to output the generated project dir into.
    """
    repo_dir = template
    import_patch = _patch_import_path_for_repo(repo_dir)

    context_file = os.path.join(repo_dir, "cookiecutter.json")

    context = generate_context(
        context_file=context_file,
        extra_context=extra_context,
    )

    # include template dir or url in the context dict
    context["cookiecutter"]["_template"] = template

    # include output+dir in the context dict
    context["cookiecutter"]["_output_dir"] = os.path.abspath(output_dir)

    # Create project from local context and project template.
    with import_patch:
        result = generate_files(
            repo_dir=repo_dir,
            context=context,
            output_dir=output_dir,
        )

    return result


class _patch_import_path_for_repo:
    def __init__(self, repo_dir):
        self._repo_dir = repo_dir
        self._path = None

    def __enter__(self):
        self._path = copy(sys.path)
        sys.path.append(self._repo_dir)

    def __exit__(self, type, value, traceback):
        sys.path = self._path
