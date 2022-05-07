"""Functions for generating a project from a project template."""
import contextlib
import errno
import json
import logging
import os
import shutil
from collections import OrderedDict

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import TemplateSyntaxError, UndefinedError

from molecule.exceptions import ContextDecodingException, UndefinedVariableInTemplate
from molecule.util import find_template, rmtree

LOG = logging.getLogger(__name__)


def apply_overwrites_to_context(context, overwrite_context):
    """Modify the given context in place based on the overwrite_context."""
    for variable, overwrite in overwrite_context.items():
        if variable not in context:
            # Do not include variables which are not used in the template
            continue

        context_value = context[variable]

        if isinstance(context_value, list):
            # We are dealing with a choice variable
            if overwrite in context_value:
                # This overwrite is actually valid for the given context
                # Let's set it as default (by definition first item in list)
                # see ``cookiecutter.prompt.prompt_choice_for_config``
                context_value.remove(overwrite)
                context_value.insert(0, overwrite)
            else:
                raise ValueError(
                    f"{overwrite} provided for choice variable {variable}"
                    f"but the choices are {context_value}."
                )
        else:
            # Simply overwrite the value for this variable
            context[variable] = overwrite


def generate_context(context_file="cookiecutter.json", extra_context=None):
    """Generate the context for a Cookiecutter project template.

    Loads the JSON file as a Python object, with key being the JSON filename.

    :param context_file: JSON file containing key/value pairs for populating
        the cookiecutter's variables.
    :param extra_context: Dictionary containing configuration overrides
    """
    context = OrderedDict([])

    try:
        with open(context_file, encoding="utf-8") as file_handle:
            obj = json.load(file_handle, object_pairs_hook=OrderedDict)
    except ValueError as e:
        # JSON decoding error.  Let's throw a new exception that is more
        # friendly for the developer or user.
        full_fpath = os.path.abspath(context_file)
        json_exc_message = str(e)
        our_exc_message = (
            f'JSON decoding error while loading "{full_fpath}".  Decoding'
            f' error details: "{json_exc_message}"'
        )
        raise ContextDecodingException(our_exc_message)

    # Add the Python object to the context dictionary
    file_name = os.path.basename(context_file)
    file_stem = os.path.splitext(file_name)[0]
    context[file_stem] = obj

    if extra_context:
        apply_overwrites_to_context(obj, extra_context)

    LOG.debug("Context generated is %s", context)
    return context


def generate_file(project_dir, infile, context, env):
    """Render filename of infile as name of outfile, handle infile correctly.

    Dealing with infile appropriately:

        a. If infile is a binary file, copy it over without rendering.
        b. If infile is a text file, render its contents and write the
           rendered infile to outfile.

    Precondition:

        When calling `generate_file()`, the root template dir must be the
        current working directory. Using `utils.work_in()` is the recommended
        way to perform this directory change.

    :param project_dir: Absolute path to the resulting generated project.
    :param infile: Input file to generate the file from. Relative to the root
        template dir.
    :param context: Dict for populating the cookiecutter's variables.
    :param env: Jinja2 template execution environment.
    """
    LOG.debug("Processing file %s", infile)

    # Render the path to the output file (not including the root project dir)
    outfile_tmpl = env.from_string(infile)

    outfile = os.path.join(project_dir, outfile_tmpl.render(**context))
    file_name_is_empty = os.path.isdir(outfile)
    if file_name_is_empty:
        LOG.debug("The resulting file name is empty: %s", outfile)
        return

    LOG.debug("Created file at %s", outfile)

    # Force fwd slashes on Windows for get_template
    # This is a by-design Jinja issue
    infile_fwd_slashes = infile.replace(os.path.sep, "/")

    # Render the file
    try:
        tmpl = env.get_template(infile_fwd_slashes)
    except TemplateSyntaxError as exception:
        # Disable translated so that printed exception contains verbose
        # information about syntax error location
        exception.translated = False
        raise
    rendered_file = tmpl.render(**context)

    # Detect original file newline to output the rendered file
    # note: newline='' ensures newlines are not converted
    with open(infile, "r", encoding="utf-8", newline="") as rd:
        rd.readline()  # Read the first line to load 'newlines' value

        # Use `_new_lines` overwrite from context, if configured.
        newline = rd.newlines
        if context["cookiecutter"].get("_new_lines", False):
            newline = context["cookiecutter"]["_new_lines"]
            LOG.debug("Overwriting end line character with %s", newline)

    LOG.debug("Writing contents to file %s", outfile)

    with open(outfile, "w", encoding="utf-8", newline=newline) as fh:
        fh.write(rendered_file)

    # Apply file permissions to output file
    shutil.copymode(infile, outfile)


@contextlib.contextmanager
def work_in(dirname=None):
    """Context manager version of os.chdir.

    When exited, returns to the working directory prior to entering.
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


def make_sure_path_exists(path):
    """Ensure that a directory exists.

    :param path: A directory path.
    """
    LOG.debug("Making sure path exists: %s", path)
    try:
        os.makedirs(path)
        LOG.debug("Created directory at: %s", path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            return False
    return True


def render_and_create_dir(dirname, context, output_dir, environment):
    """Render name of a directory, create the directory, return its path."""
    name_tmpl = environment.from_string(dirname)

    rendered_dirname = name_tmpl.render(**context)

    dir_to_create = os.path.normpath(os.path.join(output_dir, rendered_dirname))

    LOG.debug("Rendered dir %s must exist in output_dir %s", dir_to_create, output_dir)

    output_dir_exists = os.path.exists(dir_to_create)

    if output_dir_exists:
        LOG.debug("Output directory %s already exists, overwriting it", dir_to_create)
    else:
        make_sure_path_exists(dir_to_create)

    return dir_to_create, not output_dir_exists


def generate_files(
    repo_dir,
    context=None,
    output_dir=".",
):
    """Render the templates and saves them to files.

    :param repo_dir: Project template input directory.
    :param context: Dict for populating the template's variables.
    :param output_dir: Where to output the generated project dir into.
    """
    template_dir = find_template(repo_dir)
    LOG.debug("Generating project from %s...", template_dir)
    context = context or OrderedDict([])

    env = Environment(keep_trailing_newline=True, undefined=StrictUndefined)
    try:
        project_dir, delete_project_on_failure = render_and_create_dir(
            os.path.basename(template_dir),
            context,
            output_dir,
            env,
        )
    except UndefinedError as err:
        raise UndefinedVariableInTemplate(
            f"Unable to create project directory '{os.path.basename(template_dir)}'",
            err,
            context,
        )

    # We want the Jinja path and the OS paths to match. Consequently, we'll:
    #   + CD to the template folder
    #   + Set Jinja's path to '.'
    #
    #  In order to build our files to the correct folder(s), we'll use an
    # absolute path for the target folder (project_dir)

    project_dir = os.path.abspath(project_dir)
    LOG.debug("Project directory is %s", project_dir)

    with work_in(template_dir):
        env.loader = FileSystemLoader(".")

        for root, dirs, files in os.walk("."):
            for f in dirs:
                unrendered_dir = os.path.join(project_dir, root, f)
                try:
                    render_and_create_dir(unrendered_dir, context, output_dir, env)
                except UndefinedError as err:
                    if delete_project_on_failure:
                        rmtree(project_dir)
                    _dir = os.path.relpath(unrendered_dir, output_dir)
                    raise UndefinedVariableInTemplate(
                        f"Unable to create directory '{_dir}'", err, context
                    )

            for f in files:
                infile = os.path.normpath(os.path.join(root, f))
                try:
                    generate_file(project_dir, infile, context, env)
                except UndefinedError as err:
                    if delete_project_on_failure:
                        rmtree(project_dir)
                    raise UndefinedVariableInTemplate(
                        f"Unable to create file '{infile}'", err, context
                    )

    return project_dir
