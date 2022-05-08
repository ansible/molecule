# Copyright (c) 2013-2021, Audrey Roy Greenfeld
# All rights reserved.

# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:

# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.

# * Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Taken from Cookiecutter:
# https://github.com/cookiecutter/cookiecutter/blob/master/cookiecutter/main.py
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
