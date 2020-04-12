from click.testing import CliRunner

from pbench.cli.agent.commands.config import activate
from pbench.test.cli.common import capture


def test_pbench_agent_config_activate_help():
    command = ["pbench-agent-config-activate", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0


def test_pbench_agent_config_activate(monkeypatch, tmpdir):
    cfg = tmpdir / "pbench-agent.cfg"
    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()
    config = """
    [pbench-agent]
    install-dir = {}
    """.format(
        str(pbench_install_dir)
    )
    cfg.write(config)
    command = ["pbench-agent-config-activate", str(cfg)]
    out, err, exitcode = capture(command)
    pbench_result = pbench_install_dir / "config"
    assert pbench_result.exists() is True
    pbench_cfg = pbench_result / "pbench-agent.cfg"
    assert pbench_cfg.exists() is True


def test_pbench_config_activate(monkeypatch, tmpdir):
    cfg = tmpdir / "pbench-agent.cfg"
    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()
    config = """
    [pbench-agent]
    install-dir = {}
    """.format(
        str(pbench_install_dir)
    )
    cfg.write(config)

    runner = CliRunner.invoke(activate, [str(cfg)])
    assert runner.exitcode == 0
