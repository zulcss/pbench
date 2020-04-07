from click.testing import CliRunner

from pbench.cli.agent import commands


def test_help():
    runner = CliRunner()
    result = runner.invoke(commands.config_ssh_key, ["--help"])
    assert result.exit_code == 0


def test_opt_not_found():
    runner = CliRunner()
    result = runner.invoke(commands.config_ssh_key, ["-h"])
    assert result.exit_code == 2

def tst_run(tmpdir, monkeypatch):
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
    ssh_key = tmpdir / "id_rsa.pub"
    ssh_key.write("")
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
    runner = CliRunner()
    result = runner.invoke(commands.config_ssh_key, [str(cfg), str(ssh_key)])
    assert restult.exit_code == 0

    result_dir = pbench_rundir / "id-rsa"
    assert result_dir.exists()