import click

from pbench.agent.modules.cleanup import PbenchCleanup


@click.group()
def cleanup():
    pass


@cleanup.command()
def run_dir():
    PbenchCleanup().execute()


#
# Backwards compatible commands
#
@click.command()
def pbench_cleanup():
    PbenchCleanup().execute()
