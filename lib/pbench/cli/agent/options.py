import os
import sys

import click

from pbench.cli.agent import context
from pbench.agent import PbenchAgentConfig


def common_options(f):
    f = _pbench_agent_config(f)
    f = _pbench_agent_debug(f)
    f = _pbench_redis_host(f)
    return f


def _pbench_redis_host(f):
    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.redis_host = value
        return value

    return click.option(
        "--redis-host", default="localhost", callback=callback, expose_value=False,
    )(f)


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


def _pbench_agent_debug(f):
    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.debug = value
        return value

    return click.option(
        "--debug",
        is_flag=True,
        expose_value=False,
        callback=callback,
        help="Turn on debugging",
    )(f)
