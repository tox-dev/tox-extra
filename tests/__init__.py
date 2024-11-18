"""Tests."""

import functools
import os
from pathlib import Path
from typing import Any, Callable


def preserve_cwd(function: Callable) -> Callable:
    """Decorator for restoring cwd."""

    @functools.wraps(function)
    def decorator(*args: Any, **kwargs: Any):  # noqa: ANN202, ANN401
        cwd = Path.cwd()
        try:
            return function(*args, **kwargs)
        finally:
            os.chdir(cwd)

    return decorator
