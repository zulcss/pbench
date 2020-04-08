import pathlib
from pbench.agent.modules import cleanup

def test_cleanup(tmpdir, monkeypatch):
    cfg = tmpdir / "pbench-agent-config"
    pbench_rundir = tmpdir / "pbench-agent"
    pbench_rundir.mkdir()
    pbench_config = """
    [pbench-agent]
    pbench_run = {}
    """.format(
        str(pbench_rundir)
    )
    cfg.write(pbench_config)
    monkeypatch.setenv("_PBENCH_AGENT_CONFIG", str(cfg))
    pbench_rundir = pbench_rundir / "tool"
    pbench_rundir.mkdir()

    assert pbench_rundir.exists()
    c = cleanup.PbenchCleanup()
    c.cleanup()
    assert pbench_rundir.exists() == False