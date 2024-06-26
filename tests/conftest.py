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

import os
import platform
import shutil

from collections.abc import Iterable
from pathlib import Path

import pytest

from _pytest.nodes import Item
from _pytest.runner import CallInfo

from molecule.scenario import Scenario


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


@pytest.fixture(autouse=True)
def _no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable coloring output."""
    # Analyzing output with no color is much easier. Tests that need to test for
    # color output, should override the value.
    monkeypatch.setitem(os.environ, "NO_COLOR", "1")
    monkeypatch.delitem(os.environ, "PY_COLORS", raising=False)
    monkeypatch.delitem(os.environ, "ANSIBLE_FORCE_COLOR", raising=False)
    monkeypatch.delitem(os.environ, "FORCE_COLOR", raising=False)


@pytest.fixture()
def resources_folder_path() -> Path:
    """Return the path to the resources folder.

    Returns:
        Path: The path to the resources folder.
    """
    return FIXTURES_DIR / "resources"


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


def git_root() -> Path:
    """Return the root of the git repository.

    Returns:
        The root of the git repository
    """
    command = "git rev-parse --show-toplevel"
    return Path(os.popen(command, mode="r").read().strip())  # noqa: S605


@pytest.fixture(name="test_cache_path")
def fixture_test_cache_path(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> Iterable[Path]:
    """Provide a test specific cache path.

    The assumption here is that the tests are always run after being checkout out from git.
    The ephemeral directory function will be mocked to ensure that the cache directory is
    used by the test. as the ephemeral directory.

    After success completion of the test, the directory will be removed.

    Args:
        monkeypatch: The pytest monkeypatch object
        request: The pytest request object

    Yields:
        Path: The ephemeral directory
    """
    test_dir = Path(
        git_root()
        / ".cache"
        / ".molecule"
        / "tests"
        / request.path.relative_to(Path(__file__).parent).with_suffix("")
        / request.node.name,
    )
    if test_dir.exists():
        shutil.rmtree(test_dir)

    test_dir.mkdir(parents=True, exist_ok=True)

    def mock_ephemeral_directory(_self: Scenario) -> str:
        """Mock the ephemeral directory.

        Returns:
            Path: The ephemeral directory
        """
        return str(test_dir)

    monkeypatch.setattr(
        "molecule.scenario.Scenario.ephemeral_directory",
        property(mock_ephemeral_directory),
    )

    yield test_dir

    item = request.node
    if item.rep_call.failed:
        # if the test failed, keep the ephemeral directory for debugging
        return

    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture(name="test_ephemeral_dir_env")
def fixture_test_ephemeral_dir_env(test_cache_path: Path) -> dict[str, str]:
    """Provide the ephemeral directory for a given test as an env variable.

    The current path will be provided as an env variable for any subprocess commands to use
    so any commands can be found.

    Args:
        test_cache_path: The ephemeral directory path

    Returns:
        The ephemeral directory as an env variable
    """
    path = os.environ.get("PATH", "")
    return {
        "PATH": path,
        "MOLECULE_EPHEMERAL_DIRECTORY": str(test_cache_path),
    }


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Remove the test cache directory after a successful test session.

    Args:
        session: The pytest session
        exitstatus: The exit status of the test session
    """
    assert session
    if exitstatus:
        return
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return
    test_cache_dir = Path(git_root() / ".cache" / ".molecule" / "tests")
    if test_cache_dir.exists():
        shutil.rmtree(test_cache_dir)
