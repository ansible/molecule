#!/bin/bash
python3 -m setuptools_scm | awk '{print $3}'
