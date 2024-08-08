"""Bindep check feature implementations."""

from __future__ import print_function

import os
import subprocess
import sys


def check_bindep() -> None:
    """Check bindeps requirements or exit."""
    if os.path.isfile("bindep.txt"):
        # as 'bindep --profiles' does not show user defined profiles like 'test'
        # it makes no sense to list them.
        cmd = [sys.executable, "-m", "bindep", "-b", "test"]
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
            sys.exit(result.returncode)
