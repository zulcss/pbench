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

def test_clear_results(tmpdir, monkeypatch):
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
    pbench_rundir = pbench_rundir / "tools-fake"
    pbench_rundir.mkdir()

    pbench_tmpdir = pbench_rundir / "tmp"
    pbench_tmpdir.write("")

    c = cleanup.PbenchCleanup()
    c.clear_results()
    assert pbench_tmpdir.exists() == False
    assert pbench_rundir.exists() == False

def test_clear_tools_remove_default_group(tmpdir, monkeypatch):
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
    pbench_default = pbench_rundir / "tools-default"
    pbench_default.mkdir()
    pbench_default_tool = pbench_default / "perf"
    pbench_default_tool.write("")

    c = cleanup.PbenchCleanup()
    c.clear_tools()
    assert pbench_default_tool.exists() == False
    assert pbench_default.exists() == True

def test_clear_tools_remove_tool(tmpdir, monkeypatch):
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
    pbench_default = pbench_rundir / "tools-default"
    pbench_default.mkdir()
    pbench_default_tool = pbench_default / "perf"
    pbench_default_tool.write("")
    pbench_fake_tool = pbench_default / "fake"
    pbench_fake_tool.write("")

    command_args = {"tool": "fake"}
    c = cleanup.PbenchCleanup(command_args)
    c.clear_tools()

    assert pbench_fake_tool.exists() == False
    assert pbench_default_tool.exists() == True

def test_clear_tools_remove_group(tmpdir, monkeypatch):
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
    
    pbench_default = pbench_rundir / "tools-default"
    pbench_default.mkdir()
    pbench_default_tool = pbench_default / "perf"
    pbench_default_tool.write("")
    pbench_default_fake_tool = pbench_default / "fake"
    pbench_default_fake_tool.write("")

    pbench_fake_dir = pbench_rundir / "tools-fake"
    pbench_fake_dir.mkdir()
    pbench_fake_default_tool = pbench_fake_dir / "perf"
    pbench_fake_default_tool.write("")
    pbench_fake_tool = pbench_fake_dir / "fake"
    pbench_fake_tool.write("")

    command_args = {'group': "fake"}
    c = cleanup.PbenchCleanup(command_args)
    c.clear_tools()
    assert pbench_default_tool.exists() == True
    assert pbench_fake_default_tool.exists() == True
    assert pbench_fake_tool.exists() == False
    assert pbench_fake_default_tool.exists == False
