import pathlib

from pbench.agent.modules import config


def test_config_activate(tmpdir, monkeypatch):
    cfg = tmpdir / "pbench-agent-config"
    pbench_rundir = tmpdir / "pbench-agent"
    pbench_rundir.mkdir()
    pbench_config = """
    [pbench-agent]
    install-dir = {}
    """.format(
        str(pbench_rundir)
    )
    cfg.write(pbench_config)

    command_args = {"cfg_file": str(cfg)}

    c = config.PbenchToolConfig(command_args)
    c.config_activate()

    path = pathlib.Path(pbench_rundir)
    pbench_cfg = path / "config"
    assert pbench_cfg.exists()


def test_config_ssh_key(tmpdir, monkeypatch):
    cfg = tmpdir / "pbench-agent-config"
    pbench_rundir = tmpdir / "pbench-agent"
    pbench_key = tmpdir / "id_rsa.pub"
    pbench_rundir.mkdir()
    pbench_key.write("")
    pbench_config = """
    [pbench-agent]
    install-dir = {}
    """.format(
        str(pbench_rundir)
    )
    cfg.write(pbench_config)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))

    command_args = {"keyfile": str(pbench_key)}
    c = config.PbenchToolConfig(command_args)
    c.config_ssh_key()

    path = pathlib.Path(pbench_rundir)
    key = path / "id_rsa"
    assert key.exists()
