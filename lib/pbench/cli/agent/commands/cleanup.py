import errno
import shutil

import click

from pbench.agent.utils import setup_logging
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class Cleanup(base.Base):
    def execute(self):
        """Remove everyting in pbench_run"""
        self.logger = setup_logging(logfile=self.pbench_log)

        self.logger.info("Cleaning up %s", self.pbench_run)
        for path in self.pbench_run.iterdir():
            if path.name == "pbench.log":
                # Keep the log file around for debugging purposes
                continue
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                if path.is_file():
                    path.unlink()
            except OSError as err:
                if err.errno != errno.ENOENT:
                    self.logger.exception("Failed to remove %s: %s", path, err)


@click.command(
    help="clean up everything, including results and tools that have been registered"
)
@options.common_options
@context.pass_cli_context
def cleanup(ctxt):
    Cleanup(ctxt).execute()
