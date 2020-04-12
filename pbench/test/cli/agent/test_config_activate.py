from pbench.test.cli.common import capture


def test_pbench_agent_config_activate(monkeypatch, tmpdir):
    command = ["pbench-agent-config-activate", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

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
    assert pbench_result.exists()
    pbench_cfg = pbench_result / "pbench-agent.cfg"
    assert pbench_cfg.exists()


def test_pbench_config_activate(monkeypatch, tmpdir):
    command = ["pbench", "config", "activate", "--help"]
    out, err, exitcode = capture(command)
    assert exitcode == 0

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
    command = ["pbench", "config", "activate", str(cfg)]
    out, err, exitcode = capture(command)
    pbench_result = pbench_install_dir / "config"
    assert pbench_result.exists()
    pbench_cfg = pbench_result / "pbench-agent.cfg"
    assert pbench_cfg.exists()
