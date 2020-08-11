import shutil
import sys

import click

from pbench.agent.utils import setup_logging
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class Clear(base.Base):
    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        for path in self.pbench_run.iterdir():
            if not path.name.startswith("tmp") and not path.name.startswith("tools"):
                if path.is_dir():
                    shutil.rmtree(path)
                if path.is_file():
                    path.unlink()


@click.command()
@options.common_options
@context.pass_cli_context
def clear(ctxt):
    status = Clear(ctxt).execute()
    sys.exit(status)
