"""pbench-tool-meister-start

Responsible for:

   1. Starting a redis server
   2. Loading tool group data for the given tool group into the redis server
   3. Starting the tool-data-sink process
   4. Starting all the local and remote tool meisters

When complete we leave running, locally, a redis server and a tool data sink
process, and any local or remote tool meisters.

The pbench-tool-meister-stop script will take care of (gracefully) stopping
all of these processes, locally or remotely.
"""

import errno
import json
import logging
import os
import signal
import sys
import time
from distutils.spawn import find_executable
from pathlib import Path

import click
import redis

from pbench.agent.tools import ToolGroup
from pbench.cli.agent import base, context, options

# Port number is "One Tool" in hex 0x17001
# FIXME: move to common area
redis_port = 17001

# Redis server configuration template for pbench's use
redis_conf_tmpl = """bind {hostnames}
daemonize yes
dir {tm_dir}
dbfilename pbench-redis.rdb
logfile {tm_dir}/redis.log
loglevel notice
pidfile {tm_dir}/redis_{redis_port:d}.pid
port {redis_port:d}
"""

# FIXME: this should be moved to a shared area
channel = "tool-meister-chan"

# Maximum time to wait for the Redis server to respond.
REDIS_MAX_WAIT = 60


def wait_for_subs(chan, expected_tms, logger):
    """wait_for_subs - Wait for the data sink and the proper number of TMs to
    register, and when they are all registered, return a dictionary of the
    data sink and tool meister(s) pids.
    """
    pids = dict()
    have_ds = False
    num_tms = 0
    for payload in chan:
        try:
            json_str = payload["data"].decode("utf-8")
        except Exception:
            logger.warning("data payload in message not UTF-8, '%r'", json_str)
            continue
        logger.debug('channel payload, "%r"', json_str)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("data payload in message not JSON, '%s'", json_str)
            continue
        # We expect the payload to look like:
        #   { "kind": "<ds|tm>",
        #     "hostname": "<hostname>",
        #     "pid": "<pid>"
        #   }
        # Where 'kind' is either 'ds' (data-sink) or 'tm' (tool-meister),
        # 'hostname' is the host name on which that entity is running, and
        # 'pid' is that entity's PID on that host.
        try:
            new_data = dict(
                kind=data["kind"], hostname=data["hostname"], pid=data["pid"]
            )
        except KeyError:
            logger.warning("unrecognized data payload in message, '%r'", data)
            continue
        else:
            if new_data["kind"] == "ds":
                pids["ds"] = new_data
                have_ds = True
            elif new_data["kind"] == "tm":
                if "tm" not in pids:
                    pids["tm"] = []
                pids["tm"].append(new_data)
                num_tms += 1
            else:
                logger.warning("unrecognized 'kind', in data payload '%r'", data)
                continue
        if have_ds and num_tms == expected_tms:
            break
    return pids


def kill_redis_server(pid_file):
    """kill_redis_server - given a redis server PID file, attempt to KILL the
    Redis server.

    Returns "1" if successfully KILL'd; "2" if it encounters an error reading
    the PID file; "3" if bad PID value; "4" if the Redis server PID does not
    exist; "5" if some kind of OSError is encountered; and "6" if some other
    exception was encountered while KILL'ing it.
    """
    try:
        with pid_file.open("r") as fp:
            raw_pid = fp.read()
    except Exception:
        # No "pid" to kill
        return 2
    else:
        try:
            pid = int(raw_pid)
        except Exception:
            # Bad pid value
            return 3
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                # PID not found, ignore
                return 4
            else:
                # Some error encountered trying to KILL the process.
                return 5
        except Exception:
            # Some other error encountered trying to KILL the process.
            return 6
        else:
            # "successfully" KILL'd the give process.
            return 1


class Start(base.Base):
    """Main program for the tool meister start."""

    def execute(self):
        _prog = Path(sys.argv[0])
        _prog_dir = _prog.parent
        PROG = _prog.name
        logger = logging.getLogger(PROG)
        if os.environ.get("_PBENCH_TOOL_MEISTER_START_LOG_LEVEL") == "debug":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger.setLevel(log_level)
        sh = logging.StreamHandler()
        sh.setLevel(log_level)
        shf = logging.Formatter("%(message)s")
        sh.setFormatter(shf)
        logger.addHandler(sh)

        # 1. Load the tool group data given the tool group argument
        try:
            tool_group = ToolGroup(self.context.group)
        except Exception:
            logger.exception("failed to load tool group data")
            return 1

        try:
            benchmark_run_dir = os.environ["benchmark_run_dir"]
            hostname = os.environ["hostname"]
            full_hostname = os.environ["full_hostname"]
        except Exception:
            logger.exception("failed to fetch parameters from the environment")
            return 1
        else:
            tm_dir = Path(benchmark_run_dir, "tm")
            try:
                os.mkdir(tm_dir)
                os.chdir(tm_dir)
            except Exception:
                logger.exception("failed to create the local tool meister directory")
                return 1
        if not full_hostname or not hostname:
            logger.error(
                "ERROR - hostname ('%s') and full_hostname ('%s') environment"
                " variables are required",
                hostname,
                full_hostname,
            )
            return 1
        if os.environ.get("_PBENCH_UNIT_TESTS"):
            # FIXME: this is an artifact of the unit test environment.
            hostnames = "localhost"
        else:
            hostnames = f"localhost {full_hostname}"
        params = {"hostnames": hostnames, "tm_dir": tm_dir, "redis_port": redis_port}

        # 2. Start the Redis Server (config of port from agent config)
        #   - the Redis Server is requested to create the PID file

        # Create the Redis Server pbench-specific configuration file
        redis_conf = tm_dir / "redis.conf"
        redis_pid = tm_dir / f"redis_{redis_port:d}.pid"
        try:
            with redis_conf.open("w") as fp:
                fp.write(redis_conf_tmpl.format(**params))
        except Exception:
            logger.exception("failed to create redis server configuration")
            return 1
        # Start the Redis Server itself
        #   - FIXME: use podman to start a redis server container
        redis_srvr = "redis-server"
        redis_srvr_path = find_executable(redis_srvr)
        logger.debug("starting redis server")
        try:
            retcode = os.spawnl(os.P_WAIT, redis_srvr_path, redis_srvr, redis_conf)
        except Exception:
            logger.exception("failed to create redis server, daemonized")
            return 1
        else:
            if retcode != 0:
                logger.error(
                    "failed to create redis server, daemonized; return code: %d",
                    retcode,
                )
                return 1

        try:
            timeout = time.time() + REDIS_MAX_WAIT
            started_channel = "{}-start".format(channel)
            redis_connection_state = "connecting"
            redis_server = redis.Redis(host="localhost", port=redis_port, db=0)
            pubsub = redis_server.pubsub()
            while redis_connection_state == "connecting":
                try:
                    pubsub.subscribe(started_channel)
                    chan = pubsub.listen()
                    # Pull off first message which is an acknowledgement we have
                    # successfully subscribed.
                    resp = next(chan)
                except redis.exceptions.ConnectionError:
                    if time.time() > timeout:
                        raise
                    time.sleep(0.1)
                else:
                    redis_connection_state = "connected"
        except Exception as exc:
            logger.error(
                "Unable to connect to redis server, %s:%d: %r",
                "localhost",
                redis_port,
                exc,
            )
            return kill_redis_server(redis_pid)
        else:
            assert resp["type"] == "subscribe", f"bad type: f{resp!r}"
            assert resp["pattern"] is None, f"bad pattern: {resp!r}"
            assert (
                resp["channel"].decode("utf-8") == started_channel
            ), f"bad channel: {resp!r}"
            assert resp["data"] == 1, f"bad data: {resp!r}"

        # 3. Start the tool-data-sink process
        #   - leave a PID file for the tool data sink process
        #   - FIXME: use podman to start a tool-data-sink container
        tds_param_key = "tds-{}".format(self.context.group)
        tds = dict(channel=channel, benchmark_run_dir=benchmark_run_dir)
        try:
            redis_server.set(tds_param_key, json.dumps(tds, sort_keys=True))
        except Exception:
            logger.exception(
                "failed to create tool data sink parameter key in redis server"
            )
            return kill_redis_server(redis_pid)
        data_sink = "pbench-tool-data-sink"
        data_sink_path = _prog_dir / data_sink
        logger.debug("starting tool data sink")
        try:
            retcode = os.spawnl(
                os.P_WAIT,
                data_sink_path,
                data_sink,
                "localhost",
                str(redis_port),
                tds_param_key,
            )
        except Exception:
            logger.exception("failed to create pbench data sink, daemonized")
            return kill_redis_server(redis_pid)
        else:
            if retcode != 0:
                logger.error(
                    "failed to create pbench data sink, daemonized; return code: %d",
                    retcode,
                )
                return kill_redis_server(redis_pid)

        # 4. Start all the local and remote tool meister processes
        #   - leave a PID file on each local/remote host
        #   - FIXME: use podman on the remote hosts to start a tool meister
        #            container
        failures = 0
        successes = 0
        tool_meister_cmd = "pbench-tool-meister"
        tool_meister_cmd_path = _prog_dir / tool_meister_cmd
        ssh_cmd = "ssh"
        ssh_path = find_executable(ssh_cmd)
        args = [
            ssh_cmd,
            "<host replace me>",
            tool_meister_cmd,
            full_hostname,
            str(redis_port),
            "<tm param key>",
        ]
        ssh_pids = []
        for host in tool_group.hostnames.keys():
            tools = tool_group.get_tools(host)
            if host == full_hostname:
                _controller = full_hostname
            else:
                _controller = (
                    "localhost"
                    if os.environ.get("_PBENCH_UNIT_TESTS")
                    else full_hostname
                )
            tm = dict(
                benchmark_run_dir=benchmark_run_dir,
                channel=channel,
                controller=_controller,
                group=self.context.group,
                hostname=host,
                tools=tools,
            )
            tm_param_key = "tm-{}-{}".format(self.context.group, host)
            try:
                redis_server.set(tm_param_key, json.dumps(tm, sort_keys=True))
            except Exception:
                logger.exception(
                    "failed to create tool meister parameter key in redis server"
                )
                return kill_redis_server(redis_pid)
            if host == full_hostname:
                logger.debug("starting localhost tool meister")
                try:
                    retcode = os.spawnl(
                        os.P_WAIT,
                        tool_meister_cmd_path,
                        tool_meister_cmd,
                        "localhost",
                        str(redis_port),
                        tm_param_key,
                    )
                except Exception:
                    logger.exception(
                        "failed to create localhost tool meister, daemonized"
                    )
                    failures += 1
                else:
                    if retcode == 0:
                        successes += 1
                    else:
                        logger.error(
                            "failed to create localhost tool meister,"
                            " daemonized; return code: %d",
                            retcode,
                        )
                        failures += 1
                continue
            args[1] = host
            args[5] = tm_param_key
            logger.debug(
                "starting remote tool meister, ssh_path=%r args=%r", ssh_path, args
            )
            # FIXME: should we consider using Ansible instead?
            try:
                pid = os.spawnv(os.P_NOWAIT, ssh_path, args)
            except Exception:
                logger.exception(
                    "failed to create a tool meister instance for host %s", host
                )
                failures += 1
            else:
                ssh_pids.append((pid, host))
                successes += 1

        if failures > 0:
            return kill_redis_server(redis_pid)

        # Wait for all the SSH pids to complete.
        for pid, host in ssh_pids:
            try:
                exit_pid, _exit_status = os.waitpid(pid, 0)
            except OSError:
                failures += 1
                successes -= 1
                logger.exception(
                    "failed to create a tool meister instance for host %s", host
                )
            else:
                exit_status = os.WEXITSTATUS(_exit_status)
                if pid != exit_pid:
                    failures += 1
                    successes -= 1
                    logger.error(
                        "INTERNAL ERROR: os.waitpid(%d, 0) returned (%d, %d [%0X])",
                        pid,
                        exit_pid,
                        exit_status,
                        _exit_status,
                    )
                else:
                    if exit_status != 0:
                        failures += 1
                        successes -= 1
                        logger.error(
                            "failed to start tool meister on remote host '%s'"
                            " (pid %d), exit status: %d [%0X]",
                            host,
                            pid,
                            exit_status,
                            _exit_status,
                        )

        if failures > 0:
            logger.info("terminating tool meister startup due to failures")
            terminate_msg = dict(
                state="terminate", group=self.context.group, directory=None
            )
            try:
                ret = redis_server.publish(
                    channel, json.dumps(terminate_msg, sort_keys=True)
                )
            except Exception:
                logger.exception("Failed to publish terminate message")
            else:
                logger.debug("publish() = %r", ret)
            ret_val = kill_redis_server(redis_pid)
        elif successes > 0:
            # If any successes, then we need to wait for them to show up as
            # subscribers.
            logger.debug(
                "waiting for all successfully spawned SSH processes"
                " to show up as subscribers"
            )
            pids = wait_for_subs(chan, successes, logger)
            # Record our collected pids.
            try:
                redis_server.set("tm-pids", json.dumps(pids, sort_keys=True))
            except Exception:
                logger.exception("failed to set tool meister pids object")
                ret_val = kill_redis_server(redis_pid)
            else:
                ret_val = 0
        else:
            logger.warning(
                "unable to successfully start any tool meisters,"
                " but encountered no failures either: terminating"
            )
            ret_val = kill_redis_server(redis_pid)
        return ret_val


def _group(f):
    def callback(ctx, param, value):
        clictx = ctx.ensure_object(context.CliContext)
        clictx.group = value
        return value

    return click.argument(
        "group", default="default", expose_value=False, callback=callback
    )(f)


@click.command()
@options.common_options
@_group
@context.pass_cli_context
def main(ctxt):
    Start(ctxt).execute()
