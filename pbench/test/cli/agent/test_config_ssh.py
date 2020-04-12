from pbench.test.cli.common import capture


def test_pbench_agent_config_ssh_key(monkeypatch, tmpdir):
    command = ["pbench-agent-config-ssh-key", "--help"]
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
    pbench_ssh_key = tmpdir / "ssh-key"
    pbench_ssh_key.write("")
    command = ["pbench-agent-config-ssh-key", str(cfg), str(pbench_ssh_key)]
    out, err, exitcode = capture(command)
    assert exitcode == 0
    pbench_result = pbench_install_dir / "id_rsa"
    assert pbench_result.exists()


def test_pbench_config_ssh(monkeypatch, tmpdir):
    command = ["pbench", "config", "ssh", "--help"]
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
    pbench_ssh_key = tmpdir / "ssh-key"
    pbench_ssh_key.write("")
    command = ["pbench", "config", "ssh", str(cfg), str(pbench_ssh_key)]
    out, err, exitcode = capture(command)
    assert exitcode == 0
    pbench_result = pbench_install_dir / "id_rsa"
    assert pbench_result.exists()
