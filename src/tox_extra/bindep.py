"""Bindep check feature implementations."""

from __future__ import annotations

import logging
import subprocess
import sys
from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

logger = logging.getLogger(__name__)


@cache
def check_bindep(path: Path, profiles: Iterable[str] | None = None) -> None:
    """Check bindeps requirements or exit."""
    if profiles is None:  # pragma: no cover
        profiles = []
    if (path / "bindep.txt").is_file():
        # as 'bindep --profiles' does not show user defined profiles like 'test'
        # it makes no sense to list them.
        cmd = [sys.executable, "-m", "bindep", "-b", *sorted(profiles)]

        result = subprocess.run(  # noqa: S603
            cmd,
            check=False,
            text=True,
            capture_output=True,
            cwd=path,
        )
        if result.returncode:
            msg = (
                f"Running '{' '.join(cmd)}' returned {result.returncode}, "
                "likely missing system dependencies."
            )
            if result.stdout:
                msg += "\nstdout:\n" + result.stdout
            if result.stderr:
                msg += "\nstderr:\n" + result.stderr
            logger.error(msg)
            raise SystemExit(result.returncode)
