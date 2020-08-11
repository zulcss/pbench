import sys

import click

from pbench.agent.utils import setup_logging
from pbench.cli.agent.commands.tools import cli
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class List(base.Base, cli.ToolCli):
    """List the registered tools"""

    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        if self.context.group and self.context.name:
            click.secho("You cannot specify both --group and --name", fg="red")
            sys.exit(1)

        try:
            self.list_tools()
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        except KeyboardInterrupt:
            self.logger.error("Terminating...")
            return 1

        return 0


def _group_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        try:
            clictxt.group = value.split()
        except Exception:
            clictxt.group = []
        return value

    return click.option(
        "-g", "--groups", "--group", expose_value=False, callback=callback,
    )(f)


def _name_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.name = value
        return value

    return click.option(
        "-n", "--names", "--name", expose_value=False, callback=callback,
    )(f)


@click.command()
@options.common_options
@_name_option
@_group_option
@context.pass_cli_context
def list(ctxt):
    status = List(ctxt).execute()
    sys.exit(status)
