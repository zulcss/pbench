from pathlib import Path
import sys

import click

from pbench.agent.tool import ToolBase
from pbench.agent.utils import setup_logging
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class List(base.Base, ToolBase):
    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        if not self.context.group:
            self.context.group = self.groups
            for group in self.context.group:
                tg_dir = Path(self.tools_group_dir(group), "__trigger__")
                if tg_dir.exists():
                    print("%s: %s" % (group, tg_dir.read_text().strip()))
        else:
            if self.context.group not in self.groups:
                self.logger.error("bad group specified")
                return 1
            tg_dir = Path(self.tools_group_dir(self.context.group), "__trigger__")
            if tg_dir.exists():
                print("%s: %s" % (group, tg_dir.read_text().strip()))

        return 0


def _group_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.group = value
        return value

    return click.option(
        "-g", "--groups", "--group", expose_value=False, callback=callback,
    )(f)


@click.command()
@options.common_options
@_group_option
@context.pass_cli_context
def list(ctxt):
    status = List(ctxt).execute()
    sys.exit(status)
