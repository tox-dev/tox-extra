"""Unit tests."""

import os
from runpy import run_module
from unittest.mock import patch

import pytest

from . import preserve_cwd


@preserve_cwd
@pytest.mark.parametrize(
    ("folder", "expected_rc"),
    (
        pytest.param("tests/fixtures/bindep_0", 1, id="0"),
        pytest.param("tests/fixtures/bindep_1", 0, id="1"),
        pytest.param("tests/fixtures/bindep_2", 1, id="2"),
    ),
)
def test_bindep(folder: str, expected_rc: int) -> None:
    """Tests that running tox with a bindep file that is missing deps fails."""
    os.chdir(folder)
    with patch("sys.argv", ["tox"]):
        with pytest.raises(SystemExit) as exc:
            run_module("tox", run_name="__main__")
    assert exc.type == SystemExit
    assert exc.value.code == expected_rc
