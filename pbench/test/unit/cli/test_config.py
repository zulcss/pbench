import tempfile

from pbench.test.base import command


def test_pbench_config():
    out, _, exitcode = command(["pbench-config"])
    assert exitcode == 1


def test_pbench_config_help():
    out, _, exitcode = command(["pbench-config", "--help"])
    assert exitcode == 0
    assert b"show" in out
    assert b"config FILE" in out


def test_pbench_config_invalid_option():
    _, _, exitcode = command(["pbench-config", "--foo"])
    assert exitcode == 2


def test_pbench_server_dump(monkeypatch):
    FAKE_CONFIG = b"""
    [DEFAULT]
    default-host = pbench.example.com
    default-user = pbench
    default-group = pbench
    """

    with tempfile.NamedTemporaryFile() as test_config:
        test_config.write(FAKE_CONFIG)
        test_config.flush()
        monkeypatch.setenv("_PBENCH_SERVER_CONFIG", test_config.name)
        out, _, exitcode = command(["pbench-config", "-d"])
        assert exitcode == 0
        assert b"default-host" in out


def test_pbench_server_config(monkeypatch):
    FAKE_CONFIG = b"""
    [pbench-server]
    mailto = "root@localhost"
    """

    with tempfile.NamedTemporaryFile() as test_config:
        test_config.write(FAKE_CONFIG)
        test_config.flush()
        monkeypatch.setenv("_PBENCH_SERVER_CONFIG", test_config.name)
        out, _, exitcode = command(["pbench-config", "mailto", "pbench-server"])
        assert exitcode == 0
        assert b"root@localhost" in out


def test_pbench_agent_config(monkeypatch):
    FAKE_CONFIG = b"""
    [results]
    user = pbench
    """

    with tempfile.NamedTemporaryFile() as test_config:
        test_config.write(FAKE_CONFIG)
        test_config.flush()
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", test_config.name)
        out, _, exitcode = command(["pbench-config", "user", "results"])
        assert exitcode == 0
        assert b"pbench" in out


def test_pbench_config_show_section(monkeypatch):
    FAKE_CONFIG = b"""
    [results]
    user = pbench
    """

    with tempfile.NamedTemporaryFile() as test_config:
        test_config.write(FAKE_CONFIG)
        test_config.flush()
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", test_config.name)
        out, _, exitcode = command(["pbench-config", "-a", "results"])
        assert exitcode == 0
        assert b"user" in out
