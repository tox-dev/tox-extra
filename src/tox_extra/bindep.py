"""Bindep check feature implementations."""

from __future__ import annotations

import os
import subprocess
import sys
from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


@cache
def check_bindep(path: Path, profiles: Iterable[str] | None = None) -> None:
    """Check bindeps requirements or exit."""
    if profiles is None:  # pragma: no cover
        profiles = []
    if os.path.isfile(path / "bindep.txt"):
        # as 'bindep --profiles' does not show user defined profiles like 'test'
        # it makes no sense to list them.
        cmd = [sys.executable, "-m", "bindep", "-b", *sorted(profiles)]

        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=path,
        )
        if result.returncode:
            print(
                f"Running '{' '.join(cmd)}' returned {result.returncode}, "
                "likely missing system dependencies.",
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            raise SystemExit(result.returncode)
