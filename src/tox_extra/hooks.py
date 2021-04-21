"""Tox hook implementations."""
from __future__ import print_function

import logging
import os

import git

try:
    from tox import hookimpl
    from tox.reporter import error

    @hookimpl
    def tox_runtest_post(venv):
        """Hook that runs after test commands."""
        if os.path.isdir(f"{venv.envconfig.config.toxinidir}/.git"):
            _environ = dict(os.environ)
            try:
                # Force git to ignore global or user config as we do not want
                # it to consider upper level ignores that may not exist on
                # other systems.
                os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
                os.environ["XDG_CONFIG_HOME"] = "/"
                os.environ["HOME"] = "/"
                repo = git.Repo(os.getcwd())
                if repo.is_dirty(untracked_files=True):
                    error(
                        "Git reported dirty status. "
                        "Git should never report dirty status at the end of "
                        "testing, regardless if status is passed, failed or aborted."
                    )
                    os.system("git status")
                    venv.status = "failed"
            finally:
                os.environ.clear()
                os.environ.update(_environ)


except ImportError:
    # tox4
    logging.error("tox-extra disabled itself as it does not support tox4 yet.")
