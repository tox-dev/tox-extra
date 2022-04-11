"""tox_extra plugin for tox."""
import tox
from packaging.version import Version, parse

tox_version = parse(tox.__version__)
assert isinstance(tox_version, Version)

if tox_version.major == 3:
    from .tox3 import tox_addoption, tox_runtest_post  # noqa: F401

    __all__ = ["tox_addoption", "tox_runtest_post"]
elif tox_version.major == 4:
    from .tox4 import tox_add_option, tox_after_run_commands  # noqa: F401

    __all__ = ["tox_add_option", "tox_runtest_post"]
else:
    raise RuntimeError(f"tox_extra is incomptabile with tox {tox.__version__}")
