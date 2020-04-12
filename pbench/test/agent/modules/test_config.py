import pytest
from pbench.agent.modules import config


@pytest.helpers.register
def pbench_agent_install_config(monkeypatch, tmpdir, install_dir):
    pbench_cfg = tmpdir / "pbench-argent.cfg"
    config = """
    [pbench-agent]
    install-dir = {}
    """.format(
        str(install_dir)
    )
    pbench_cfg.write(config)
    return str(pbench_cfg)


def test_config_activate(monkeypatch, tmpdir):
    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()

    pbench_cfg = pbench_agent_install_config(monkeypatch, tmpdir, pbench_install_dir)

    command_args = {"config": pbench_cfg}
    config.AgentUtilConfig(command_args).execute()
    pbench_install_dir = pbench_install_dir / "config"
    assert pbench_install_dir.exists()


def test_config_ssh_key(monkeypatch, tmpdir):
    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()

    pbench_cfg = pbench_agent_install_config(monkeypatch, tmpdir, pbench_install_dir)
    pbench_key = tmpdir / "id_rsa"
    pbench_key.write("")

    command_args = {"config": pbench_cfg, "ssh_key": str(pbench_key)}
    config.ConfigSSHKey(command_args).execute()
    pbench_dest_key = pbench_install_dir / "id_rsa"
    assert pbench_dest_key.exists()
