"""Plugin implementation for tox4"""
from argparse import ArgumentParser
from typing import List

# pylint: disable=no-name-in-module
# pylint: disable=import-error
from tox.execute import Outcome
from tox.plugin import impl
from tox.tox_env.api import ToxEnv
from tox.tox_env.errors import Fail

from .common import MSG_GIT_DIRTY, is_git_dirty


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
