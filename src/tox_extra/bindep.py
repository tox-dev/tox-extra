"""Bindep check feature implementations."""

from __future__ import print_function

import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

if sys.version_info >= (3, 9):  # pragma: no cover
    from functools import cache
else:  # pragma: no cover
    cache = lru_cache(maxsize=None)


@cache
def check_bindep(path: Path, profiles: Optional[Iterable[str]] = None) -> None:
    """Check bindeps requirements or exit."""
    if profiles is None:  # pragma: no cover
        profiles = []
    if os.path.isfile(path / "bindep.txt"):
        # as 'bindep --profiles' does not show user defined profiles like 'test'
        # it makes no sense to list them.
        cmd = [sys.executable, "-m", "bindep", "-b", *sorted(profiles)]
        # # determine profiles
        # result = subprocess.run(
        #     [sys.executable, "-m", "bindep", "--profiles"],
        #     check=False,
        #     universal_newlines=True,
        #     stdout=subprocess.PIPE,
        # )
        # if result.returncode:
        #     print("Bindep failed to list profiles: %s", result.stdout)
        #     sys.exit(result.returncode)
        # lines = result.stdout.splitlines()
        # try:
        #     profiles = lines[lines.index("Configuration profiles:") + 1 :]
        #     if "test" in profiles:
        #         cmd.append("test")
        # except ValueError:
        #     pass

        result = subprocess.run(
            cmd,
            check=False,
            universal_newlines=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            cwd=path,
        )
        if result.returncode:
            print(
                f"Running '{' '.join(cmd)}' returned {result.returncode}, "
                "likely missing system dependencies."
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            raise SystemExit(result.returncode)
