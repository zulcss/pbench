from click.testing import CliRunner

from pbench.cli.agent import commands


def test_help():
    runner = CliRunner()
    result = runner.invoke(commands.config_activate, ["--help"])
    assert result.exit_code == 0


def test_opt_not_found():
    runner = CliRunner()
    result = runner.invoke(commands.config_activate, ["-h"])
    assert result.exit_code == 2


def test_run(tmpdir, monkeypatch):
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
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
    runner = CliRunner()
    result = runner.invoke(commands.config_activate, [str(cfg)])
    assert result.exit_code == 0

    result_dir = pbench_rundir / "config" / "pbench-agent-config"
    assert result_dir.exists()

