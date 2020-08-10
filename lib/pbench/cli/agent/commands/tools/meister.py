"""pbench-tool-meister

Handles the life-cycle executing a given tool on a host. The tool meister
performs the following operations:

  1. Ensures the given tool exists with the supported version
  2. Fetches the parameters configured for the tool
  3. Waits for the message to start the tool
     a. Messages contain three pieces of information:
        the next operational state to move to, the tool group being for which
        the operation will be applied, and the directory in which the tool-
        data-sink will collect and store all the tool data during send
        operations
  4. Waits for the message to stop the tool
  5. Waits for the message to send the tool data remotely
  6. Repeats steps 3 - 5 until a "terminate" message is received

If a SIGTERM or SIGQUIT signal is sent to the tool meister, any existing
running tool is shutdown, all local data is removed, and the tool meister
exits.

A redis [1] instance is used as the communication mechanism between the
various tool meisters on nodes and the benchmark driver. The redis instance is
used both to communicate the initial data set describing the tools to use, and
their parameteres, for each tool meister, as well as a pub/sub for
coordinating starts and stops of all the tools.

The tool meister is given two arguments when started: the redis server to use,
and the redis key to fetch its configuration from for its operation.

[1] https://redis.io/

$ sudo dnf install python3-redis
$ sudo pip3 install python-daemon
$ sudo pip3 install python-pidfile
"""

import json
import logging
import os
import sys

import click
import daemon
import pidfile
import redis

from pbench.agent.meister import Terminate, ToolMeister
from pbench.cli.agent import base, context, options


def _redis_host(f):
    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.redis_host = value
        return value

    return click.argument("redis_host", expose_value=False, callback=callback)(f)


def _redis_port(f):
    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.redis_port = value
        return value

    return click.argument("redis_port", expose_value=False, callback=callback)(f)


def _param_key(f):
    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.param_key = value
        return value

    return click.argument("param_key", expose_value=False, callback=callback)(f)


class Meister(base.Base):
    """Main program for the tool meister.

    This class is the simple driver for the tool meister behaviors,
    handling setup of signals, Redis() client construction, loading and
    validating parameters.
    """

    def execute(self):
        PROG = os.path.basename(sys.argv[0])
        pbench_bin = self.pbench_install_dir

        logger = logging.getLogger(PROG)
        fh = logging.FileHandler(f"{self.context.param_key}.log")
        if os.environ.get("_PBENCH_UNIT_TESTS"):
            fmtstr = "%(levelname)s %(name)s %(funcName)s -- %(message)s"
        else:
            fmtstr = (
                "%(asctime)s %(levelname)s %(process)s %(thread)s"
                " %(name)s %(funcName)s %(lineno)d -- %(message)s"
            )
        fhf = logging.Formatter(fmtstr)
        fh.setFormatter(fhf)
        if os.environ.get("_PBENCH_TOOL_MEISTER_LOG_LEVEL") == "debug":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        fh.setLevel(log_level)
        logger.addHandler(fh)
        logger.setLevel(log_level)

        try:
            redis_server = redis.Redis(
                host=self.context.redis_host, port=self.context.redis_port, db=0
            )
        except Exception as e:
            logger.error(
                "Unable to connect to redis server, %s:%s: %s",
                self.context.redis_host,
                self.context.redis_port,
                e,
            )
            return 2

        try:
            params_raw = redis_server.get(self.context.param_key)
            if params_raw is None:
                logger.error(
                    'Parameter key, "%s" does not exist.', self.context.param_key
                )
                return 3
            logger.info("params_key (%s): %r", self.context.param_key, params_raw)
            params_str = params_raw.decode("utf-8")
            params = json.loads(params_str)
            # Validate the tool meister parameters without constructing an object
            # just yet, as we want to make sure we can talk to the redis server
            # before we go through the trouble of daemonizing below.
            ToolMeister.fetch_params(params)
        except Exception as exc:
            logger.error(
                "Unable to fetch and decode parameter key, '%s': %s",
                self.context.param_key,
                exc,
            )
            return 4
        else:
            redis_server.connection_pool.disconnect()
            del redis_server

        pidfile_name = f"{self.context.param_key}.pid"
        pfctx = pidfile.PIDFile(pidfile_name)
        with daemon.DaemonContext(
            stdout=sys.stdout,
            stderr=sys.stderr,
            working_directory=os.getcwd(),
            umask=0o022,
            pidfile=pfctx,
            files_preserve=[sys.stdout, sys.stderr, fh.stream.fileno()],
        ):
            try:
                # Previously we validated the tool meister parameters, and in
                # doing so made sure we had proper access to the redis server.
                #
                # We can safely create the ToolMeister object now that we are
                # "daemonized".
                logger.debug("constructing Redis() object")
                try:
                    # NOTE: we have to recreate the connection to the redis
                    # service since all open file descriptors were closed as part
                    # of the daemonizing process.
                    redis_server = redis.Redis(
                        host=self.context.redis_host, port=self.context.redis_port, db=0
                    )
                except Exception as e:
                    logger.error(
                        "Unable to connect to redis server, %s:%s: %s",
                        self.context.redis_host,
                        self.context.redis_port,
                        e,
                    )
                    return 2
                else:
                    logger.debug("constructed Redis() object")

                try:
                    tm = ToolMeister(pbench_bin, params, redis_server, logger)
                except Exception:
                    logger.exception(
                        "Unable to re-construct the ToolMeister"
                        ' object with parms, "%r"',
                        params,
                    )
                    return 4

                terminate = False
                try:
                    while not terminate:
                        try:
                            logger.debug("waiting ...")
                            action, data = tm.wait_for_command()
                            logger.debug("acting ... %r, %r", action, data)
                            failures = action(data)
                            if failures > 0:
                                logger.warning(
                                    "%d failures encountered for action, '%r',"
                                    " on data, '%r'",
                                    failures,
                                    action,
                                    data,
                                )
                        except Terminate:
                            logger.info("terminating")
                            terminate = True
                except Exception:
                    logger.exception("Unexpected error encountered")
                finally:
                    tm.cleanup()
            finally:
                logger.info("Remove pid file ... (%s)", pidfile_name)
                try:
                    os.unlink(pidfile_name)
                except Exception:
                    logger.exception("Failed to remove pid file %s", pidfile_name)

        return 0


@click.command()
@options.common_options
@_redis_host
@_redis_port
@_param_key
@context.pass_cli_context
def main(ctxt):
    Meister(ctxt).execute()
