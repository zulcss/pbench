import sys

import click
import six


class CliContext:
    def initialize(self):
        if six.PY2:
            click.secho("python3 required, either directly or through SCL", err="red")
            sys.exit(1)


pass_cli_context = click.make_pass_decorator(CliContext, ensure=True)
