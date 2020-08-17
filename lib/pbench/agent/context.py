import click


class CliContext:
    """Inialize an empty click object"""

    def initialize(self):
        self.debug = False


pass_cli_context = click.make_pass_decorator(CliContext, ensure=True)
