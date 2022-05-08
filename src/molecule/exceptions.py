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
# https://github.com/cookiecutter/cookiecutter/blob/master/cookiecutter/exceptions.py
"""All exceptions used in the Cookiecutter code base are defined here."""


class MoleculeException(Exception):
    """
    Base exception class.

    All Molecule-specific exceptions should subclass this class.
    """


class NonTemplatedInputDirException(MoleculeException):
    """
    Exception for when a project's input dir is not templated.

    The name of the input directory should always contain a string that is
    rendered to something else, so that input_dir != output_dir.
    """


class ContextDecodingException(MoleculeException):
    """
    Exception for failed JSON decoding.

    Raised when a project's JSON context file can not be decoded.
    """


class UndefinedVariableInTemplate(MoleculeException):
    """
    Exception for out-of-scope variables.

    Raised when a template uses a variable which is not defined in the
    context.
    """

    def __init__(self, message, error, context):
        """Exception for out-of-scope variables."""
        self.message = message
        self.error = error
        self.context = context

    def __str__(self):
        """Text representation of UndefinedVariableInTemplate."""
        return (
            f"{self.message}. "
            f"Error message: {self.error.message}. "
            f"Context: {self.context}"
        )
