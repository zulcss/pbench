import click
import click_completion
import pbr.version

from pbench.cli.agent.commands import cleanup
from pbench.cli.agent.commands import config

click_completion.init()


@click.group()
@click.version_option(version=pbr.version.VersionInfo("pbench"))
@click.pass_context
def main(ctxt):
    """
    A benchmarking and performance analysis framework.

    For more help: https://distributed-system-analysis.github.io/

    To enable autocomplete:
     eval "$(_PBENCH_COMPLETE=source pbench)"
    """
    pass


main.add_command(cleanup.cleanup)
main.add_command(config.config)
