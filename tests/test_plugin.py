"""Hosts tests for the plugin."""

import os
from pathlib import Path
from runpy import run_module
from subprocess import PIPE, check_output, run

import pytest

from . import preserve_cwd

TOX_SAMPLE = """
[tox]
skipsdist = true
"""


@preserve_cwd
def test_fail_if_dirty(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Validated that it fails when drity."""
    # We need to mock sys.argv because run_module will look at it and fail
    # as the argv received of pytest would leak into our tox module call.
    monkeypatch.setattr("sys.argv", ["tox"])

    path = Path(tmp_path)
    os.chdir(path)

    # add tox.ini and .gitignore files (untracked)
    with open(Path(tmp_path) / "tox.ini", "w", encoding="utf-8") as file:
        file.write(TOX_SAMPLE)

    # check running tox w/o git repo is passing
    with pytest.raises(SystemExit) as exc:
        run_module("tox", run_name="__main__")  # , alter_sys=True)
    assert exc.type == SystemExit
    assert exc.value.code == 0

    # create temp git repository
    run("git init --initial-branch=main", shell=True, check=True)
    run("git add --all", shell=True, check=True)
    run(
        "git commit --allow-empty -m 'Empty initial commit'",
        shell=True,
        check=True,
        cwd=tmp_path,
    )
    output = check_output("git status --porcelain", shell=True, universal_newlines=True)
    assert output == ""

    with open(Path(tmp_path) / ".gitignore", "w", encoding="utf-8") as file:
        file.write(".tox\n")

    result = run(
        "git status --porcelain",
        shell=True,
        universal_newlines=True,
        cwd=tmp_path,
        stdout=PIPE,
        check=False,
    )
    assert result.returncode == 0
    assert "?? .gitignore" in result.stdout

    # check plugin is installed
    result = run(
        "python -m tox --version",
        shell=True,
        universal_newlines=True,
        stdout=PIPE,
        check=False,
    )
    assert result.returncode == 0
    assert "tox-extra" in result.stdout

    # check tox is failing while dirty
    # We use runpy to call tox in order to assure that coverage happens, as
    # running a subprocess would prevent it from working.
    with pytest.raises(SystemExit) as exc:
        run_module("tox", run_name="__main__", alter_sys=True)
    assert exc.type == SystemExit
    assert exc.value.code == 1

    # add untracked files
    run("git add .", shell=True, check=True)
    run("git commit -m 'Add untracked files'", shell=True, check=True)

    # check that tox is now passing
    with pytest.raises(SystemExit) as exc:
        run_module("tox", run_name="__main__", alter_sys=True)
    assert exc.type == SystemExit
    assert exc.value.code == 0
