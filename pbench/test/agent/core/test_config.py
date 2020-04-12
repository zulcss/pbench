import pytest

from pbench.agent.core.config import AgentConfig


@pytest.helpers.register
def pbench_agent_env_config(tmpdir, monkeypatch, config):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_cfg.write(config)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    return str(pbench_cfg)


@pytest.helpers.register
def pbench_agent_config(tmpdir, config):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_cfg.write(config)
    return str(pbench_cfg)


def test_config_with_error():
    with pytest.raises(Exception):
        AgentConfig()


# def test_config_invalid_config_path():
#    with pytest.raises(Exception):
#        AgentConfig(config_file='/fake')


def test_config_invalid_path(monkeypatch):
    with pytest.raises(Exception):
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", "/fake")
        AgentConfig()


def test_config_defaults(mocker, monkeypatch, tmpdir):
    mock_exists = mocker.patch("pathlib.Path.exists")
    mock_exists.return_value = True
    mock_mkdir = mocker.patch("pathlib.Path.mkdir")
    mock_mkdir.return_value = True

    pbench_agent_env_config(tmpdir, monkeypatch, "")
    c = AgentConfig()
    assert c.get_pbench_run() == "/var/lib/pbench-agent"
    assert c.get_pbench_tmp() == "/var/lib/pbench-agent/tmp"
    assert c.get_pbench_log() == "/var/lib/pbench-agent/pbench.log"
    assert c.get_install_dir() == "/opt/pbench-agent"


# def test_valid_config_env(monkeypatch, tmpdir):
#    pbench_cfg = pbench_agent_env_config(tmpdir, monkeypatch, "")
#    c = AgentConfig()
#    assert c.config == str(pbench_cfg)


def test_cfg_get_pbench_run_env(monkeypatch, tmpdir):
    cfg = """
    [pbench-agent]
    pbench_run = /tmp
    """
    pbench_agent_env_config(tmpdir, monkeypatch, cfg)
    c = AgentConfig()
    assert c.get_pbench_run() == "/tmp"


def test_pbench_run_not_exists_env(mocker, monkeypatch, tmpdir):
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


def test_get_pbench_tmp_env(monkeypatch, tmpdir):
    pbench_dir = tmpdir / "pbench-agent"
    pbench_dir.mkdir()
    cfg = """
    [pbench-agent]
    pbench_run = {}
    """.format(
        str(pbench_dir)
    )
    pbench_agent_env_config(tmpdir, monkeypatch, cfg)
    c = AgentConfig()
    assert c.get_pbench_tmp() == str(pbench_dir) + "/tmp"


def test_get_pbench_log_env(monkeypatch, tmpdir):
    pbench_log_dir = tmpdir / "pbench-test"
    pbench_log_dir.mkdir()
    cfg = """
    [pbench-agent]
    pbench_log = {}
    """.format(
        str(pbench_log_dir)
    )
    pbench_agent_env_config(tmpdir, monkeypatch, cfg)
    c = AgentConfig()
    assert c.get_pbench_log() == str(pbench_log_dir) + "/pbench.log"


def test_get_install_dir_env(monkeypatch, tmpdir):
    pbench_install_dir = tmpdir / "pbench-test"
    pbench_install_dir.mkdir()
    cfg = """
    [pbench-agent]
    install-dir: {}
    """.format(
        str(pbench_install_dir)
    )
    pbench_agent_env_config(tmpdir, monkeypatch, cfg)
    c = AgentConfig()
    assert c.get_install_dir() == str(pbench_install_dir)
