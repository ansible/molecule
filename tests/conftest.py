#  Copyright (c) 2015-2018 Cisco Systems, Inc.  # noqa: D100
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

import contextlib
import os
import platform
import random
import shutil
import string

from collections.abc import Iterable
from pathlib import Path

import pytest

from _pytest.nodes import Item
from _pytest.runner import CallInfo
from filelock import FileLock

from molecule import config as molecule_config
from molecule.scenario import ephemeral_directory


FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Marker to skip tests on macos when running on GH
mac_on_gh = pytest.mark.skipif(
    platform.system() == "Darwin" and "CI" in os.environ,
    reason="Podman and docker not currently available for macOS on Github",
)


def is_subset(subset, superset):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    # Checks if first dict is a subset of the second one
    if isinstance(subset, dict):
        return all(
            key in superset and is_subset(val, superset[key])  # type: ignore[no-untyped-call]
            for key, val in subset.items()
        )

    if isinstance(subset, list | set):
        return all(
            any(is_subset(subitem, superitem) for superitem in superset)  # type: ignore[no-untyped-call]
            for subitem in subset
        )

    # assume that subset is a plain value if none of the above match
    return subset == superset


@pytest.fixture(name="random_string")
def fixture_random_string(l=5):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, E741, D103
    return "".join(random.choice(string.ascii_uppercase) for _ in range(l))  # noqa: S311


@contextlib.contextmanager
def change_dir_to(dir_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    cwd = os.getcwd()  # noqa: PTH109
    os.chdir(dir_name)
    yield
    os.chdir(cwd)


@pytest.fixture()
def temp_dir(tmpdir, random_string, request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    directory = tmpdir.mkdir(random_string)

    with change_dir_to(directory.strpath):
        yield directory


@pytest.fixture()
def resources_folder_path() -> Path:
    """Return the path to the resources folder.

    Returns:
        Path: The path to the resources folder.
    """
    return FIXTURES_DIR / "resources"


def molecule_project_directory() -> str:  # noqa: D103
    return os.getcwd()  # noqa: PTH109


def molecule_directory() -> str:  # noqa: D103
    return molecule_config.molecule_directory(molecule_project_directory())


def molecule_scenario_directory() -> str:  # noqa: D103
    return os.path.join(molecule_directory(), "default")  # noqa: PTH118


def molecule_file() -> str:  # noqa: D103
    return get_molecule_file(molecule_scenario_directory())


def get_molecule_file(path: str) -> str:  # noqa: D103
    return molecule_config.molecule_file(path)


def molecule_ephemeral_directory(_fixture_uuid) -> str:  # type: ignore[no-untyped-def]  # noqa: ANN001, D103
    project_directory = f"test-project-{_fixture_uuid}"
    scenario_name = "test-instance"

    return ephemeral_directory(
        os.path.join("molecule_test", project_directory, scenario_name),  # noqa: PTH118
    )


def pytest_collection_modifyitems(items, config):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    marker = config.getoption("-m")
    is_sharded = False
    shard_id = 0
    shards_num = 0
    if not marker.startswith("shard_"):
        return
    shard_id, _, shards_num = marker[6:].partition("_of_")
    if shards_num:
        shard_id = int(shard_id)
        shards_num = int(shards_num)
        is_sharded = True
    else:
        raise ValueError("shard_{}_of_{} marker is invalid")  # noqa: EM101, TRY003
    if not is_sharded:
        return
    if not 0 < shard_id <= shards_num:
        raise ValueError(  # noqa: TRY003
            "shard_id must be greater than 0 and not bigger than shards_num",  # noqa: EM101
        )
    for test_counter, item in enumerate(items):
        cur_shard_id = test_counter % shards_num + 1
        marker = getattr(pytest.mark, f"shard_{cur_shard_id}_of_{shards_num}")
        item.add_marker(marker)
    del marker
    print(f"Running sharded test group #{shard_id} out of {shards_num}")


@pytest.fixture(autouse=True)
def reset_pytest_vars(monkeypatch):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT004
    """Make PYTEST_* env vars inaccessible to subprocesses."""
    for var_name in tuple(os.environ):
        if var_name.startswith("PYTEST_"):
            monkeypatch.delenv(var_name, raising=False)


@pytest.fixture(autouse=True)
def block_on_serial_mark(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, PT004, D103
    # https://github.com/pytest-dev/pytest-xdist/issues/385
    os.makedirs(".tox", exist_ok=True)  # noqa: PTH103
    if request.node.get_closest_marker("serial"):
        with FileLock(".tox/semaphore.lock"):
            yield
    else:
        yield


@pytest.fixture()
def test_fixture_dir(request: pytest.FixtureRequest) -> Path:
    """Provide the fixture directory for a given test.

    :param request: The pytest request object
    :returns: The fixture directory
    """
    return FIXTURES_DIR / request.path.relative_to(Path(__file__).parent).with_suffix("")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(  # type: ignore[misc]
    item: Item,
    call: CallInfo[None],  # noqa: ARG001
) -> pytest.TestReport:
    """Create a phase report for each test phase.

    Allows the test success or failure to be available in a fixture
    https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures

    Args:
        item: The pytest item
        call: The pytest call
    Returns:
        The pytest report
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture(name="test_ephemeral_dir_path")
def fixture_test_ephemeral_dir_path(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> Iterable[Path]:
    """Provide the ephemeral directory for a given test.

    The assumption here is that the tests are always run after being checkout out from git.
    We will monkey patch the source and provide it as an env for any subprocess commands to use.

    After success completion of the test, the directory will be removed.

    Args:
        monkeypatch: The pytest monkeypatch object
        request: The pytest request object

    Yields:
        Path: The ephemeral directory
    """
    # use the git root as the ephemeral directory
    command = "git rev-parse --show-toplevel"
    git_root = Path(os.popen(cmd=command, mode="r").read().strip())
    test_dir = Path(
        git_root
        / ".cache"
        / ".molecule"
        / "tests"
        / request.path.relative_to(Path(__file__).parent).with_suffix("")
        / request.node.name,
    )
    if test_dir.exists():
        shutil.rmtree(test_dir)

    test_dir.mkdir(parents=True, exist_ok=True)

    def mock_ephemeral_directory() -> Path:
        """Mock the ephemeral directory.

        Returns:
            Path: The ephemeral directory
        """
        return test_dir

    monkeypatch.setattr("molecule.scenario.Scenario.ephemeral_directory", mock_ephemeral_directory)

    yield test_dir

    item = request.node
    if item.rep_call.failed:
        # if the test failed, keep the ephemeral directory for debugging
        return

    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture(name="test_ephemeral_dir_env")
def fixture_test_ephemeral_dir_env(test_ephemeral_dir_path: Path) -> dict[str, str]:
    """Provide the ephemeral directory for a given test as an env variable.

    The current path will be provided as an env variable for any subprocess commands to use
    so any commands can be found.

    Args:
        test_ephemeral_dir_path: The ephemeral directory path

    Returns:
        The ephemeral directory as an env variable
    """
    path = os.environ.get("PATH", "")
    return {
        "PATH": path,
        "MOLECULE_EPHEMERAL_DIRECTORY": str(test_ephemeral_dir_path),
    }
