# Example curl command sequence
#
#   $ md5sum tool-data.tar.xz > tool-data.tar.xz.md5
#   $ curl -X PUT -H "MD5SUM: $(awk '{print $1}' tool-data.tar.xz.md5)" \
#     http://localhost:8080/tool-data/XXX...XXX/perf48.example.com \
#     --data-binary @tool-data.tar.xz

# Needs daemon, pidfile, and bottle
#   sudo dnf install python3-bottle python3-daemon
#   sudo pip3 install python-pidfile

import errno
import json
import logging
import os
import sys
from pathlib import Path

import click
import daemon
import pidfile
import redis

from pbench.agent.sink import ToolDataSink
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


class Sink(base.Base):
    def execute(self):
        PROG = Path(sys.argv[0]).name

        logger = logging.getLogger(PROG)
        fh = logging.FileHandler(f"{PROG}.log")
        if os.environ.get("_PBENCH_UNIT_TESTS"):
            fmtstr = "%(levelname)s %(name)s %(funcName)s -- %(message)s"
        else:
            fmtstr = (
                "%(asctime)s %(levelname)s %(process)s %(thread)s"
                " %(name)s %(funcName)s %(lineno)d -- %(message)s"
            )
        fhf = logging.Formatter(fmtstr)
        fh.setFormatter(fhf)
        if os.environ.get("_PBENCH_TOOL_DATA_SINK_LOG_LEVEL") == "debug":
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
            # The expected parameters for this "data-sink" is what "channel" to
            # subscribe to for the tool meister operational life-cycle.  The
            # data-sink listens for the state transitions, start | stop | send |
            # terminate, exiting when "terminate" is received, marking the state
            # in which data is captured.
            #
            # E.g. params = '{ "channel": "run-chan",
            #                  "benchmark_run_dir": "/loo/goo" }'
            params = json.loads(params_str)
            channel = params["channel"]
            benchmark_run_dir = Path(params["benchmark_run_dir"]).resolve(strict=True)
        except Exception as ex:
            logger.error(
                "Unable to fetch and decode parameter key, %s: %s",
                self.context.param_key,
                ex,
            )
            return 4
        else:
            if not benchmark_run_dir.is_dir():
                logger.error(
                    "Run directory argument, %s, must be a real" " directory.",
                    benchmark_run_dir,
                )
                return 5
            logger.debug("Tool Data Sink parameters check out, daemonizing ...")
            redis_server.connection_pool.disconnect()
            del redis_server

        pidfile_name = f"{PROG}.pid"
        pfctx = pidfile.PIDFile(pidfile_name)
        with open(f"{PROG}.out", "w") as sofp, open(f"{PROG}.err", "w") as sefp:
            with daemon.DaemonContext(
                stdout=sofp,
                stderr=sefp,
                working_directory=os.getcwd(),
                umask=0o022,
                pidfile=pfctx,
                files_preserve=[fh.stream.fileno()],
            ):
                try:
                    # We have to re-open the connection to the redis server now that we
                    # are "daemonized".
                    logger.debug("constructing Redis() object")
                    try:
                        redis_server = redis.Redis(
                            host=self.context.redis_host,
                            port=self.context.redis_port,
                            db=0,
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

                    tds_app = ToolDataSink(
                        redis_server, channel, benchmark_run_dir, logger
                    )
                    tds_app.execute()
                except OSError as exc:
                    if exc.errno == errno.EADDRINUSE:
                        logger.error(
                            "ERROR - tool data sink failed to start, localhost:8080 already in use"
                        )
                    else:
                        logger.exception("ERROR - failed to start the tool data sink")
                except Exception:
                    logger.exception("ERROR - failed to start the tool data sink")
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
    Sink(ctxt).execute()
