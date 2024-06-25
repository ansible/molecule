import os
import shlex
import subprocess

from pathlib import Path


def test_success(tmpdir: Path) -> None:
    command = 'ansible localhost -m debug -a \'msg={{ lookup("ansible.builtin.env", "PWD") }}\''

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        check=False,
        text=True,
        cwd=tmpdir,
    )

    ansible_pwd = result.stdout.splitlines()[1].split(":")[1].strip().strip('"')

    assert ansible_pwd == str(tmpdir)


def test_fail(tmpdir: Path) -> None:
    command = 'ansible localhost -m debug -a \'msg={{ lookup("ansible.builtin.env", "PWD") }}\''

    env = {"PATH": os.environ["PATH"]}

    result = subprocess.run(
        shlex.split(command),
        shell=False,
        capture_output=True,
        check=False,
        text=True,
        env=env,
        cwd=tmpdir,
    )

    ansible_pwd = result.stdout.splitlines()[1].split(":")[1].strip().strip('"')

    assert ansible_pwd == ""
    assert ansible_pwd != str(tmpdir)
