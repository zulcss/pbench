import sys

import click

from pbench.agent import context
from pbench.agent.tools.base import ToolBase


class List(ToolBase):
    def __init__(self, context):
        super(List, self).__init__(context)

    def execute(self):
        self.list()
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
@_name_option
@_group_option
@context.pass_cli_context
def list(ctxt):
    status = List(ctxt).execute()
    sys.exit(status)
