from pbench.agent.modules.config import AgentUtilConfig


def test_config_activate(monkeypatch, tmpdir):
    pbench_install = tmpdir / "pbench-test"
    pbench_install.mkdir()
    pbench_cfg = tmpdir / "pbench-argent.cfg"
    config = """
    [pbench-agent]
    install-dir = {}
    """.format(
        pbench_install
    )
    pbench_cfg.write(config)

    command_args = {"config": str(pbench_cfg)}
    AgentUtilConfig(command_args).execute()
    pbench_install_dir = pbench_install / "config"
    assert pbench_install_dir.exists()
