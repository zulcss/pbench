import click
import click_completion
import pbr.version

from pbench.cli.agent.commands import cleanup
from pbench.cli.agent.commands import config
from pbench.cli.agent.commands import meister
from pbench.cli.agent.commands import tools
from pbench.cli.agent.commands import triggers
from pbench.cli.agent.commands import results

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
main.add_command(meister.meister)
main.add_command(tools.tools)
main.add_command(triggers.triggers)
main.add_command(results.results)
