import pathlib

import pytest

from pbench.agent.core import utils


def test_syserror():
    with pytest.raises(SystemExit) as e:
        utils.sysexit()

    assert 1 == e.value.code


def test_normalize_path():
    p = pathlib.Path("/tmp")
    assert utils.normalize_path(p) == "/tmp"
