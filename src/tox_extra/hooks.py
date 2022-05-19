"""Tox hook implementations."""
import os
from argparse import ArgumentParser

import git

MSG_GIT_DIRTY = (
    "Git reported dirty status. "
    "Git should never report dirty status at the end of "
    "testing, regardless if status is passed, failed or aborted."
)


def is_git_dirty(path: str) -> bool:
    """Reports if the git repository at the given path is dirty."""
    if os.path.isdir(f"{path}/.git"):
        _environ = dict(os.environ)
        try:
            repo = git.Repo(os.getcwd())
            if repo.is_dirty(untracked_files=True):
                os.system("git status")
                os.system("git diff -U0 --minimal")
                return True
        finally:
            os.environ.clear()
            os.environ.update(_environ)
    return False


try:  # tox3 support
    from tox import config, hookimpl
    from tox.reporter import error

    @hookimpl
    def tox_addoption(parser: config.Parser) -> None:
        """Add a command line option to the tox parser."""
        parser.add_argument(
            "--allow-dirty",
            action="store_true",
            default=False,
            help="If it should allow git to report dirty after executing commands.",
        )

    @hookimpl
    def tox_runtest_post(venv):
        """Hook that runs after test commands."""
        allow_dirty = getattr(venv.envconfig.config.option, "allow_dirty", False)
        if not allow_dirty and is_git_dirty(venv.envconfig.config.toxinidir):
            venv.status = "failed"
            error(MSG_GIT_DIRTY)

except ImportError as exc:  # tox4 support
    print(exc)
    from typing import List

    from tox.execute import Outcome
    from tox.plugin import impl
    from tox.tox_env.api import ToxEnv
    from tox.tox_env.errors import Fail

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
    def tox_after_run_commands(
        tox_env: ToxEnv, exit_code: int, outcomes: List[Outcome]
    ) -> None:
        """Hook that runs after test commands."""
        allow_dirty = getattr(tox_env.options, "allow_dirty", False)
        if not allow_dirty and is_git_dirty("."):
            raise Fail(MSG_GIT_DIRTY)
