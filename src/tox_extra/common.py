"""Shared code for tox_extra."""
import os

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
                return True
        finally:
            os.environ.clear()
            os.environ.update(_environ)
    return False
