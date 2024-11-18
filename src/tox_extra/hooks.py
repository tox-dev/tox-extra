"""Tox hook implementations."""

from __future__ import annotations

import logging
import os
import pathlib
import shutil
import sys
from typing import TYPE_CHECKING, Any

import git
from tox.plugin import impl
from tox.tox_env.errors import Fail
from tox.tox_env.python.api import Python

from tox_extra.bindep import check_bindep

if TYPE_CHECKING:
    from argparse import ArgumentParser

    from tox.execute import Outcome
    from tox.tox_env.api import ToxEnv


logger = logging.getLogger(__name__)
WARNING_MSG_GIT_DIRTY = (
    "'git status -s' reported dirty. "
    "Modify .gitignore file as this will cause an error under CI/CD pipelines."
)

ERROR_MSG_GIT_DIRTY = (
    "::error title=tox-extra detected git dirty status:: " + WARNING_MSG_GIT_DIRTY
)


def is_git_dirty(path: str) -> bool:
    """Reports if the git repository at the given path is dirty."""
    git_path = shutil.which("git")
    if pathlib.Path(f"{path}/.git").is_dir():
        _environ = dict(os.environ)
        try:
            repo = git.Repo(pathlib.Path.cwd())
            if repo.is_dirty(untracked_files=True):
                # stderr is hidden to avoid noise like occasional:
                # warning: untracked cache is disabled on this system or location
                os.system(f"{git_path} status -s 2>/dev/null")  # noqa: S605
                # We want to display long diff only on non-interactive shells,
                # like CI/CD pipelines because on local shell, the user can
                # decide to run it himself if the status line was not enogh.
                if not os.isatty(sys.stdout.fileno()):
                    os.system(f"{git_path} --no-pager diff -U0 --minimal")  # noqa: S605
                return True
        finally:
            os.environ.clear()
            os.environ.update(_environ)
    return False


@impl
def tox_add_option(parser: ArgumentParser) -> None:
    """Add a command line option to the tox parser."""
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        default=False,
        help="If it should allow git to report dirty after executing commands.",
    )


@impl
# pylint: disable=unused-argument
def tox_on_install(
    tox_env: ToxEnv,
    arguments: Any,  # noqa: ARG001,ANN401
    section: str,  # noqa: ARG001
    of_type: str,  # noqa: ARG001
) -> None:
    """Runs just before installing package."""
    if os.environ.get("TOX_EXTRA_BINDEP", "1") != "0":
        profiles = {
            "test",
            tox_env.name,  # exact tox env name, useful for stuff like 'docs' or 'lint'
            *tox_env.name.split("-"),
        }
        if isinstance(tox_env, Python):
            profiles.add(f"python{tox_env.py_dot_ver()}")  # python3.12 like profile
            profiles.add(
                f"py{tox_env.py_dot_ver().replace('.', '')}",
            )  # py312 like profile

        check_bindep(path=pathlib.Path.cwd(), profiles=frozenset(profiles))


@impl
# pylint: disable=unused-argument
def tox_after_run_commands(
    tox_env: ToxEnv,
    exit_code: int,  # noqa: ARG001
    outcomes: list[Outcome],  # noqa: ARG001
) -> None:
    """Hook that runs after test commands."""
    allow_dirty = getattr(tox_env.options, "allow_dirty", False)
    if not allow_dirty and is_git_dirty("."):
        if os.environ.get("CI") == "true":
            raise Fail(ERROR_MSG_GIT_DIRTY)
        logger.error(WARNING_MSG_GIT_DIRTY)
