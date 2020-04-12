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
    """.format(str(pbench_run))
    pbench_cfg.write(config)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(pbench_cfg))
    return pbench_run

@pytest.helpers.register
def stub_pbench_dirs(tmpdir, install_dir):
    pbench_install_dir = install_dir / "tools-defaults"
    pbench_install_dir.mkdir()
    pbench_tool = pbench_install_dir / "ocp"
    pbench_tool.write("")

def test_pbench_cleanup(monkeypatch, tmpdir):
    pbench_run_dir = pbench_agent_run(monkeypatch, tmpdir)
    stub_pbench_dirs(tmpdir, pbench_run_dir)

    cleanup.PbenchCleanup().execute()
    assert len([p for p in pathlib.Path(pbench_run_dir).iterdir()]) == 0
