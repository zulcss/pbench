import click

from pbench.agent import context
from pbench.agent.tools.base import ToolBase


class Clear(ToolBase):
    def __init__(self, context):
        super(Clear, self).__init__(context)

    def execute(self):

        status = self.clear()
        return status


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


def _name_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.name = []
        if value:
            clictxt.name.append(value)
        return value

    return click.option(
        "-n", "--names", "--name", expose_value=False, callback=callback,
    )(f)


def _remotes_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        try:
            clictxt.remotes = value.split(",") if "," in value else [value]
        except Exception:
            clictxt.remotes = []
        return value

    return click.option(
        "-r", "--remotes", "--remote", expose_value=False, callback=callback,
    )(f)


@click.command(help="clear regisered tools")
@_name_option
@_group_option
@_remotes_option
@context.pass_cli_context
def clear(ctxt):
    Clear(ctxt).execute()
