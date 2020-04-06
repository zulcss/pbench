import configparser
import pathlib

import pytest

from pbench.agent.config import AgentConfig
from pbench.common import exception


class TestAgentConfig(object):
    def test_get_agent_env(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench_agent]
        install_dir = /tmp
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        try:
            AgentConfig()
        except:  # noqa:E722
            assert False
        else:
            assert True

    def test_missing_agent_env(self, tmpdir):
        with pytest.raises(exception.BrokenConfig):
            AgentConfig()

    def test_invalid_agent_config(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        []
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        with pytest.raises(configparser.MissingSectionHeaderError):
            AgentConfig()

    def test_pbench_get(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        install_dir = /tmp
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get("pbench-agent", "install_dir") == "/tmp"

    def test_pbench_get_run(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        pbench_run = /tmp
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_run() == "/tmp"

    def test_missing_pbench_get_run(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        pbench_install = /tmp
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_run() == "/var/lib/pbench-agent"

    def test_pbench_tmp_dir(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_run = tmpdir / "pbench_run"
        pbench_run.mkdir()
        pbench_config = """
        [pbench-agent]
        pbench_run = {}
        """.format(
            str(pbench_run)
        )
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_tmp() == str(pbench_run / "tmp")

    def test_pbench_tmp_dir_missing(self, mocker, monkeypatch, tmpdir):
        mock_mkdir = mocker.patch("pathlib.Path.mkdir")
        mock_mkdir.return_value = True
        path_exists = mocker.patch("pathlib.Path.exists")
        path_exists.return_value = True

        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert pathlib.Path.exists(c.get_pbench_tmp())

    def test_get_pbench_log_file(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        pbench_log = /tmp
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_log() == "/tmp/pbench.log"

    def test_invalid_pbench_log_file(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_log() == "/var/lib/pbench-agent/pbench.log"

    def test_get_pbench_install_dir(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        install-dir = /tmp
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_install_dir() == "/tmp"

    def test_get_pbench_install_dir_invalid(self, monkeypatch, tmpdir):
        cfg = tmpdir / "pbench-agent-config"
        pbench_config = """
        [pbench-agent]
        """
        cfg.write(pbench_config)
        monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
        c = AgentConfig()
        assert c.get_pbench_install_dir() == "/opt/pbench-agent"
