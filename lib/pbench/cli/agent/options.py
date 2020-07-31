import os
import sys

import click

from pbench.cli.agent import context
from pbench.agent import PbenchAgentConfig


def common_options(f):
    f = _pbench_agent_config(f)
    return f


def _pbench_agent_config(f):
    """Option for agent configuration"""

    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        try:
            if value is None or not os.path.exists(value):
                click.secho(f"Configuration file is not found: {value}", err="Red")
                sys.exit(1)

            clictx.config = PbenchAgentConfig(value)
        except Exception as ex:
            click.secho(f"Failed to load {value}: {ex}", err="red")
            sys.exit(1)
        return value

    return click.option(
        "-C",
        "--config",
        envvar="_PBENCH_AGENT_CONFIG",
        type=click.Path(exists=True),
        callback=callback,
        expose_value=False,
        help=(
            "Path to a pbench-agent config. If provided pbench will load "
            "this config file first. By default is looking for config in "
            "'_PBENCH_AGENT_CONFIG' envrionment variable."
        ),
    )(f)
