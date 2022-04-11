"""Plugin implementation for tox3"""
from tox import config, hookimpl
from tox.reporter import error

from .common import MSG_GIT_DIRTY, is_git_dirty


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
