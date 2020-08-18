import sys

import click

from pbench.agent import context
from pbench.agent.triggers.base import TriggerBase


class List(TriggerBase):
    def __init__(self, context):
        super(List, self).__init__(context)

    def execute(self):
        self.list()


def _group_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.group = value
        return value

    return click.option(
        "-g", "--groups", "--group", expose_value=False, callback=callback,
    )(f)


@click.command()
@_group_option
@context.pass_cli_context
def list(ctxt):
    status = List(ctxt).execute()
    sys.exit(status)
