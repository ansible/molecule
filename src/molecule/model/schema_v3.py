#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#
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
"""Schema v3 Validation Module."""

import json
import logging
import os

from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError

from molecule import api
from molecule.data import __file__ as data_module

LOG = logging.getLogger(__name__)


def validate(c):
    """Perform schema validation."""
    result = []
    schemas = []

    schema_files = [os.path.dirname(data_module) + "/molecule.json"]
    driver_name = c["driver"]["name"]

    driver_schema_file = None
    if driver_name in api.drivers():
        driver_schema_file = api.drivers()[driver_name].schema_file()

    if driver_schema_file is None:
        msg = f"Driver {driver_name} does not provide a schema."
        LOG.warning(msg)
    elif not os.path.exists(driver_schema_file):
        msg = f"Schema {driver_schema_file} for driver {driver_name} not found."
        LOG.warning(msg)
    else:
        schema_files.append(driver_schema_file)

    for schema_file in schema_files:
        with open(schema_file, encoding="utf-8") as f:
            schema = json.load(f)
        schemas.append(schema)

    for schema in schemas:
        try:
            jsonschema_validate(c, schema)
        except ValidationError as exc:
            # handle validation error for driver name
            if exc.json_path == "$.driver.name" and exc.message.endswith(
                (
                    "is not of type 'string'",
                    "is not valid under any of the given schemas",
                ),
            ):
                wrong_driver_name = str(exc.message.split()[0])
                driver_name_err_msg = exc.schema["messages"]["anyOf"]
                result.append(f"{wrong_driver_name} {driver_name_err_msg}")
            else:
                result.append(exc.message)

    return result
