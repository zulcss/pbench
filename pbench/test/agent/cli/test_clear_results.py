from click.testing import CliRunner

from pbench.cli.agent import commands

def test_cleanup_help():
    runner = CliRunner()
    result = runner.invoke(commands.clear_results, ["--help"])
    assert result.exit_code == 0

def test_cleanup_invalid():
    runner = CliRunner()
    result = runner.invoke(commands.clear_results, ["--foo"])
    assert result.exit_code == 2