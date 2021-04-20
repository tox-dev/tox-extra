"""Hosts tests for the plugin."""
import functools
import os
import types
from pathlib import Path
from runpy import run_module
from subprocess import PIPE, check_output, run

import pytest
from tox import __version__ as tox_version

TOX_SAMPLE = """
[tox]
skipsdist = true
"""

tox3_only = pytest.mark.skipif(not tox_version.startswith("3."), reason="requires tox3")
tox4_only = pytest.mark.skipif(not tox_version.startswith("4."), reason="requires tox4")


def preserve_cwd(function):
    """Decorator for restoring cwd."""

    @functools.wraps(function)
    def decorator(*args, **kwargs):
        cwd = os.getcwd()
        try:
            return function(*args, **kwargs)
        finally:
            os.chdir(cwd)

    return decorator


@tox3_only
def test_import_hook() -> None:
    """One placeholder test."""
    # pylint: disable=import-outside-toplevel
    from tox_extra.hooks import tox_runtest_post

    assert isinstance(tox_runtest_post, types.FunctionType)


@tox3_only
@preserve_cwd
def test_fail_if_dirty(tmp_path) -> None:
    """Validated that it fails when drity."""
    path = Path(tmp_path)
    os.chdir(path)

    # add tox.ini and .gitignore files (untracked)
    open(Path(tmp_path) / "tox.ini", "w").write(TOX_SAMPLE)

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

    open(Path(tmp_path) / ".gitignore", "w").write(".tox\n")

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
    if tox_version.startswith("3."):
        assert exc.value.code == 1
    else:
        # This plugin is not expected to do anything with tox4 yet, but we
        # want to be sure it does not break it.
        assert exc.value.code == 0
    # add untracked files
    run("git add .", shell=True, check=True)
    run("git commit -m 'Add untracked files'", shell=True, check=True)

    # check that tox is now passing
    with pytest.raises(SystemExit) as exc:
        run_module("tox", run_name="__main__", alter_sys=True)
    assert exc.type == SystemExit
    assert exc.value.code == 0
