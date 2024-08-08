"""Tests."""

import functools
import os


def preserve_cwd(function):
    """Decorator for restoring cwd."""

    @functools.wraps(function)
    def decorator(*args, **kwargs):
        cwd = os.getcwd()
        try:
            return function(*args, **kwargs)
        finally:
            os.chdir(cwd)

    return decorator
