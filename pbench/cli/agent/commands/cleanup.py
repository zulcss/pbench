import click

from pbench.agent.modules.cleanup import PbenchCleanup, PbenchClearResults


@click.group()
def cleanup():
    pass


@cleanup.command()
def run_dir():
    PbenchCleanup().execute()


@cleanup.command()
def results():
    PbenchClearResults().execute()


#
# Backwards compatible commands
#
@click.command()
def pbench_cleanup():
    PbenchCleanup().execute()


@click.command()
def pbench_clear_results():
    PbenchClearResults().execute()
