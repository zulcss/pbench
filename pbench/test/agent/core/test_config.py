import pytest

from pbench.agent.core.config import AgentConfig


def test_config_with_no_env():
    with pytest.raises(Exception):
        AgentConfig()


def test_config_invalid_path(monkeypatch):
    with pytest.raises(Exception):
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", "/fake")
        AgentConfig()


def test_valid_config(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_cfg.write("")
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.config == str(pbench_cfg)


def test_default_get_pbench_run(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_cfg.write("")
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_pbench_run() == "/var/lib/pbench-agent"


def test_cfg_get_pbench_run(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    cfg = """
    [pbench-agent]
    pbench_run = /tmp
    """
    pbench_cfg.write(cfg)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_pbench_run() == "/tmp"


def test_pbench_run_not_exists(mocker, monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    cfg = """
    [pbench-agent]
    pbench_run = /fake
    """
    pbench_cfg.write(cfg)
    m = mocker.patch("pathlib.Path.exists")
    m.return_value = False
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    with pytest.raises(Exception):
        c = AgentConfig()
        c.get_pbench_run()


def test_get_pbench_tmp(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_tmp_dir = tmpdir / "pbench-test"
    pbench_tmp_dir.mkdir()
    cfg = """
    [pbench-agent]
    pbench_run = {}
    """.format(
        str(pbench_tmp_dir)
    )
    pbench_cfg.write(cfg)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_pbench_tmp() == str(pbench_tmp_dir) + "/tmp"


def test_get_pbench_log(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_log_dir = tmpdir / "pbench-test"
    pbench_log_dir.mkdir()
    cfg = """
    [pbench-agent]
    pbench_log = {}
    """.format(
        str(pbench_log_dir)
    )
    pbench_cfg.write(cfg)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_pbench_log() == str(pbench_log_dir) + "/pbench.log"


def test_invalid_get_pbench_log(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_log_dir = tmpdir / "pbench-test"
    pbench_log_dir.mkdir()
    cfg = """
    """
    pbench_cfg.write(cfg)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_pbench_log() == "/var/lib/pbench-agent/pbench.log"


def test_invalid_get_install_dir(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_install_dir = tmpdir / "pbench-test"
    pbench_install_dir.mkdir()
    cfg = """
    """
    pbench_cfg.write(cfg)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_install_dir() == "/opt/pbench-agent"


def test_get_install_dir(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_install_dir = tmpdir / "pbench-test"
    pbench_install_dir.mkdir()
    cfg = """
    [pbench-agent]
    install-dir: {}
    """.format(
        str(pbench_install_dir)
    )
    pbench_cfg.write(cfg)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    c = AgentConfig()
    assert c.get_install_dir() == str(pbench_install_dir)
