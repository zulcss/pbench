from pathlib import Path
import sys

import click

from pbench.agent.tool import ToolBase
from pbench.agent.utils import setup_logging
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class Register(base.Base, ToolBase):
    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        trigger = Path(self.tools_group_dir(self.context.group), "__trigger__")
        if trigger.exists():
            trigger.unlink()
        trigger.write_text("%s:%s\n" % (self.context.start, self.context.stop))
        return 0


def _group_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.group = value
        return value

    return click.option(
        "-g",
        "--groups",
        "--group",
        default="default",
        expose_value=False,
        callback=callback,
    )(f)


def _start_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        if ":" in value:
            click.secho(f'the start trigger cannot have a colon in it: "%s"', value)
            sys.exit(1)
        clictxt.start = value
        return value

    return click.option(
        "--start-trigger", required=True, expose_value=False, callback=callback,
    )(f)


def _stop_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        if ":" in value:
            click.secho(f'the stop trigger cannot have a colon in it: "%s"', value)
            sys.exit(1)
        clictxt.stop = value
        return value

    return click.option(
        "--stop-trigger", required=True, expose_value=False, callback=callback,
    )(f)


@click.command()
@options.common_options
@_group_option
@_start_option
@_stop_option
@context.pass_cli_context
def register(ctxt):
    status = Register(ctxt).execute()
    sys.exit(status)
