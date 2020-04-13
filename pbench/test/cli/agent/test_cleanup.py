import pathlib

import pytest

from pbench.test.cli.common import capture


@pytest.helpers.register
def pbench_run_config(monkeypatch, tmpdir, install_dir):
    cfg = tmpdir / "pbench-agent.cfg"
    config = """
    [pbench-agent]
    pbench_run = {}
    """.format(
        str(install_dir)
    )
    cfg.write(config)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
    return install_dir


@pytest.helpers.register
def stub_pbench_run_dir(tmpdir, install_dir):
    default_group = install_dir / "tools-default"
    default_group.mkdir()
    fake_tool = default_group / "ocp"
    fake_tool.write("")


def test_pbench_cleanup(monkeypatch, tmpdir):
    command = ["pbench-cleanup", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()
    install_dir = pbench_run_config(monkeypatch, tmpdir, pbench_install_dir)
    stub_pbench_run_dir(tmpdir, pbench_install_dir)

    command = ["pbench-cleanup"]
    out, err, exitcode = capture(command)
    pbench_result = pathlib.Path(install_dir)
    assert len([p for p in pbench_result.iterdir()]) == 0


def test_cli_pbench_cleanup(monkeypatch, tmpdir):
    command = ["pbench", "cleanup", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()
    install_dir = pbench_run_config(monkeypatch, tmpdir, pbench_install_dir)
    stub_pbench_run_dir(tmpdir, pbench_install_dir)

    command = ["pbench", "cleanup", "run-dir"]
    out, err, exitcode = capture(command)
    pbench_result = pathlib.Path(install_dir)
    assert len([p for p in pbench_result.iterdir()]) == 0


def test_pbench_clear_results(monkeypatch, tmpdir):
    command = ["pbench-clear-results", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()
    run_dir = pbench_run_config(monkeypatch, tmpdir, pbench_install_dir)
    stub_pbench_run_dir(tmpdir, run_dir)

    command = ["pbench-clear-results"]
    out, err, exitcode = capture(command)
    assert exitcode == 0


def test_cli_pbench_cleanup_results(monkeypatch, tmpdir):
    command = ["pbench", "cleanup", "results", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()
    run_dir = pbench_run_config(monkeypatch, tmpdir, pbench_install_dir)
    stub_pbench_run_dir(tmpdir, run_dir)

    command = ["pbench", "cleanup", "results"]
    out, err, exitcode = capture(command)
    assert exitcode == 0


def test_pbench_clear_tools(monkeypatch, tmpdir):
    command = ["pbench-clear-tools", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()

    run_dir = pbench_run_config(monkeypatch, tmpdir, pbench_install_dir)
    stub_pbench_run_dir(tmpdir, run_dir)
    pbench_fake_group = run_dir / "fake-group"
    pbench_fake_group.mkdir()
    pbench_fake_tool = run_dir / "ocp"
    pbench_fake_tool.write("")

    command = ["pbench-clear-tools"]
    out, err, exitcode = capture(command)
    assert exitcode == 0

    pbench_result = run_dir / "tools-default" / "ocp"
    assert pbench_result.exists() is False


def test_pbench_cli_clear_tools(monkeypatch, tmpdir):
    command = ["pbench", "cleanup", "tools", "--help"]
    out, err, exitcode = capture(command)
    assert b"--help" in out
    assert exitcode == 0

    pbench_install_dir = tmpdir / "pbench-agent"
    pbench_install_dir.mkdir()

    run_dir = pbench_run_config(monkeypatch, tmpdir, pbench_install_dir)
    stub_pbench_run_dir(tmpdir, run_dir)
    pbench_fake_group = run_dir / "fake-group"
    pbench_fake_group.mkdir()
    pbench_fake_tool = run_dir / "ocp"
    pbench_fake_tool.write("")

    command = ["pbench", "cleanup", "tools"]
    out, err, exitcode = capture(command)
    assert exitcode == 0

    pbench_result = run_dir / "tools-default" / "ocp"
    assert pbench_result.exists() is False
