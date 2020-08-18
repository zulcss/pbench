import sys

import click

from pbench.agent import context
from pbench.agent.triggers.base import TriggerBase


class Register(TriggerBase):
    def __init__(self, context):
        super(Register, self).__init__(context)

    def execute(self):
        self.register()

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
@_group_option
@_start_option
@_stop_option
@context.pass_cli_context
def register(ctxt):
    status = Register(ctxt).execute()
    sys.exit(status)
