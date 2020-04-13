import pathlib
import pytest

from pbench.agent.modules import cleanup


@pytest.helpers.register
def pbench_agent_run(monkeypatch, tmpdir):
    pbench_cfg = tmpdir / "pbench-agent.cfg"
    pbench_run = tmpdir / "pbench-agent"
    pbench_run.mkdir()
    config = """
    [pbench-agent]
    pbench_run = {}
    """.format(
        str(pbench_run)
    )
    pbench_cfg.write(config)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    return pbench_run


@pytest.helpers.register
def stub_pbench_dirs(tmpdir, run_dir):
    pbench_run_dir = run_dir / "tools-default"
    pbench_run_dir.mkdir()
    pbench_tool = pbench_run_dir / "ocp"
    pbench_tool.write("")


def test_pbench_cleanup(monkeypatch, tmpdir):
    pbench_run_dir = pbench_agent_run(monkeypatch, tmpdir)
    stub_pbench_dirs(tmpdir, pbench_run_dir)

    cleanup.PbenchCleanup().execute()
    assert len([p for p in pathlib.Path(pbench_run_dir).iterdir()]) == 0


def test_pbench_clear_tools_default(monkeypatch, tmpdir):
    pbench_run_dir = pbench_agent_run(monkeypatch, tmpdir)
    stub_pbench_dirs(tmpdir, pbench_run_dir)

    cleanup.PbenchClearTools().execute()
    pbench_run_dir = pbench_run_dir / "tools-default"
    assert len([p for p in pathlib.Path(pbench_run_dir).iterdir()]) == 0


def test_pbench_clear_tools_with_tool_name(monkeypatch, tmpdir):
    pbench_run_dir = pbench_agent_run(monkeypatch, tmpdir)
    stub_pbench_dirs(tmpdir, pbench_run_dir)

    pbench_fake_group = pbench_run_dir / "fake-group"
    pbench_fake_group.mkdir()
    pbench_fake_tool = pbench_run_dir / "ocp"
    pbench_fake_tool.write("")

    command_args = {"tool": "ocp"}
    cleanup.PbenchClearTools(command_args).execute()
    pbench_run_dir = pbench_run_dir / "tools-default"
    assert len([p for p in pathlib.Path(pbench_run_dir).iterdir()]) == 0
    assert len([p for p in pathlib.Path(pbench_fake_group).iterdir()]) == 0


def test_pbench_clear_tools_with_group(monkeypatch, tmpdir):
    pbench_run_dir = pbench_agent_run(monkeypatch, tmpdir)
    stub_pbench_dirs(tmpdir, pbench_run_dir)

    pbench_fake_group = pbench_run_dir / "fake-group"
    pbench_fake_group.mkdir()
    pbench_fake_tool = pbench_run_dir / "ocp"
    pbench_fake_tool.write("")

    command_args = {"group": "fake-group"}
    cleanup.PbenchClearTools(command_args).execute()
    pbench_run_dir = pbench_run_dir / "tools-default"
    assert len([p for p in pathlib.Path(pbench_run_dir).iterdir()]) == 1
    assert len([p for p in pathlib.Path(pbench_fake_group).iterdir()]) == 0
