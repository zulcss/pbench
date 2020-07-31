import click
import click_completion
import pbr.version

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
