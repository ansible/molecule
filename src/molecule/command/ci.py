#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
"""CI log folding handlers."""

import functools
import os
import time

from molecule.console import console


def wrap_for_ci(func):
    """Wrap the execute_subcommand to provide log folding when running in CI services."""
    is_travis = os.getenv("TRAVIS")
    is_github_actions = os.getenv("GITHUB_ACTIONS")
    is_gitlab_ci = os.getenv("GITLAB_CI")
    if not is_travis and not is_github_actions and not is_gitlab_ci:
        return func

    if is_travis:

        @functools.wraps(func)
        def ci_wrapper(config, subcommand):
            scenario = config.scenario.name
            console.print(
                f"travis_fold:start:{scenario}.{subcommand}",
                f"[ci_info]Molecule[/] [scenario]{scenario}[/] > [action]{subcommand}[/]",
                sep="",
                markup=True,
                emoji=False,
                highlight=False,
            )
            try:
                return func(config, subcommand)
            finally:
                console.print(
                    f"travis_fold:end:{scenario}.{subcommand}",
                    markup=False,
                    emoji=False,
                    highlight=False,
                )

    elif is_github_actions:

        @functools.wraps(func)
        def ci_wrapper(config, subcommand):
            scenario = config.scenario.name
            console.print(
                "::group::",
                f"[ci_info]Molecule[/] [scenario]{scenario}[/] > [action]{subcommand}[/]",
                sep="",
                markup=True,
                emoji=False,
                highlight=False,
            )
            try:
                return func(config, subcommand)
            finally:
                console.print("::endgroup::", markup=True, emoji=False, highlight=False)

    elif is_gitlab_ci:

        @functools.wraps(func)
        def ci_wrapper(config, subcommand):
            scenario = config.scenario.name
            # GitLab requres:
            #  - \r (carriage return)
            #  - \e[0K (clear line ANSI escape code. We use \033 for the \e escape char)
            clear_line = "\r\033[0K"
            console.print(
                f"section_start:{int(time.time())}:{scenario}.{subcommand}",
                end=clear_line,
                markup=False,
                emoji=False,
                highlight=False,
            )
            console.print(
                # must be one color for the whole line or gitlab sets odd widths to each word.
                f"[ci_info]Molecule {scenario} > {subcommand}[/]",
                end="\n",
                markup=True,
                emoji=False,
                highlight=False,
            )
            try:
                return func(config, subcommand)
            finally:
                console.print(
                    f"section_end:{int(time.time())}:{scenario}.{subcommand}",
                    end=f"{clear_line}\n",
                    markup=False,
                    emoji=False,
                    highlight=False,
                )

    return ci_wrapper
