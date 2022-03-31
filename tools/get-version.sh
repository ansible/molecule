#!/bin/bash
set -e
{
    python3 -c "import setuptools_scm" || python3 -m pip install --user setuptools-scm
} 1>&2  # redirect stdout to stderr to avoid polluting the output
python3 -m setuptools_scm | \
    sed 's/Guessed Version\([^+]\+\).*/\1/'
