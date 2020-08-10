import os
import time
import json
import tempfile
import subprocess
import shutil
import requests
import requests.exceptions
import hashlib

from pathlib import Path
from pbench.server.utils import md5sum
from pbench.agent.tools import Tool


class Terminate(Exception):
    """Simple exception to be raised when the tool meister main loop should exit
    gracefully.
    """

    pass


class ToolMeisterError(Exception):
    """Simple exception for any errors from the ToolMeister class.
    """

    pass


class ToolMeister(object):
    """Encapsulate tool life-cycle

    The goal of this class is to make sure all necessary state and behaviors
    for managing a given tool are handled by the methods offered by the
    class.

    The start_, stop_, send_, and wait_ prefixed methods represent all the
    necessary interfaces for managing the life-cycle of a tool.  The cleanup()
    method is provided to abstract away any necessary clean up required by a
    tool so that the main() driver does not need to know any details about a
    tool.

    The format of the JSON data for the parameters is as follows:

        {
            "benchmark_run_dir":  "<Top-level directory of the current"
                          " benchmark run>",
            "channel":    "<Redis server channel name to subscribe to for"
                          " start/stop/send messages from controller>",
            "controller": "<hostname of the controller driving all the tool"
                          " miesters; if this tool meister is running locally"
                          " with the controller, then it does not need to send"
                          " data to the tool data sink since it can access the"
                          " ${benchmark_run_dir} and ${benchmark_results_dir}"
                          " directories directly.>",
            "group":      "<Name of the tool group from which the following"
                          " tools data was pulled, passed as the"
                          " --group argument to the individual tools>",
            "hostname":   "<hostname of tool meister, should be same as"
                          " 'hostname -f' where tool meister is running>",
            "tools": {
                "tool-0": [ "--opt-0", "--opt-1", ..., "--opt-N" ],
                "tool-1": [ "--opt-0", "--opt-1", ..., "--opt-N" ],
                ...,
                "tool-N": [ "--opt-0", "--opt-1", ..., "--opt-N" ]
            }
        }

    Each action message should contain three pieces of data: the state to
    move to, either start, stop, or send, the tool group to apply that action to,
    and the directory in which to store the data. In JSON form it will look
    like:

        {
            "state":     "<'start'|'stop'|'send'>",
            "group":     "<tool group name>",
            "directory": "<directory in which to store tool data>"
        }

    If the Tool Meister is running on the same host as the pbench agent
    controller, then the Tool Meister will write is data directly to the
    ${benchmark_results_dir} using the controller's host name; if the Tool
    Meister is running remotely, then it will use a temporary directory under
    ${benchmark_run_dir}, and will send the data to the Tool Data Sink during
    the "send" phase.
    """

    @staticmethod
    def fetch_params(params):
        """Static help method that allows the method constructing a ToolMeister
        instance to verify the parameters before we actually construct the
        object.

        The definition of the contents of a parameter block is really
        independent of a ToolMeister implementation, but we keep this method
        in the ToolMeister class since it is closely related to the
        implementation.
        """
        try:
            benchmark_run_dir = params["benchmark_run_dir"]
            channel = params["channel"]
            controller = params["controller"]
            group = params["group"]
            hostname = params["hostname"]
            tools = params["tools"]
        except KeyError as exc:
            raise ToolMeisterError(f"Invalid parameter block, missing key {exc}")
        else:
            return benchmark_run_dir, channel, controller, group, hostname, tools

    def __init__(self, pbench_bin, params, redis_server, logger):
        self.logger = logger
        self.pbench_bin = pbench_bin
        ret_val = self.fetch_params(params)
        (
            self._benchmark_run_dir,
            self._channel,
            self._controller,
            self._group,
            self._hostname,
            self._tools,
        ) = ret_val
        self._running_tools = dict()
        self._rs = redis_server
        logger.debug("pubsub")
        self._pubsub = self._rs.pubsub()
        logger.debug("subscribe %s", self._channel)
        self._pubsub.subscribe(self._channel)
        logger.debug("listen")
        self._chan = self._pubsub.listen()
        logger.debug("done listening")
        # Name of the temporary tool data directory to use when invoking
        # tools.  This is a local temporary directory when the Tool Meister is
        # remote from the pbench controller.
        if self._controller != self._hostname:
            self._tmp_dir = Path(
                tempfile.mkdtemp(
                    dir=self._benchmark_run_dir,
                    prefix=f"tm.{self._group}.{os.getpid()}.",
                )
            )
        else:
            self._tmp_dir = None
        # Now that we have subscribed the channel as specified in the params
        # object, we need to pull off the first message, which is an
        # acknowledgement that we have properly subscribed.
        logger.debug("next")
        resp = next(self._chan)
        assert resp["type"] == "subscribe", f"Unexpected 'type': {resp!r}"
        assert resp["pattern"] is None, f"Unexpected 'pattern': {resp!r}"
        assert (
            resp["channel"].decode("utf-8") == self._channel
        ), f"Unexpected 'channel': {resp!r}"
        assert resp["data"] == 1, f"Unexpected 'data': {resp!r}"
        logger.debug("next done")
        # First state we are expecting
        self.state = "start"
        self._state_trans = {
            "start": {"next": "stop", "action": self.start_tools},
            "stop": {"next": "send", "action": self.stop_tools},
            "send": {"next": "start", "action": self.send_tools},
        }
        self._valid_states = frozenset(["start", "stop", "send", "terminate"])
        for key in self._state_trans.keys():
            assert (
                key in self._valid_states
            ), f"INTERNAL ERROR: invalid state transition entry, '{key}'"
            assert self._state_trans[key]["next"] in self._valid_states, (
                "INTERANL ERROR: invalie state transition next entry for"
                f" '{key}', '{self._state_trans[key]['next']}'"
            )
        self._message_keys = frozenset(["directory", "group", "state"])
        # The current 'directory' into which the tools are collected; not set
        # until a 'start tools' is executed, cleared when a 'send tools'
        # completes.
        self._directory = None

        # FIXME: run all the "--install" commands for the tools to ensure
        # they are successful before declaring that we are ready.

        # Tell the entity that started us who we are, indicating we're ready.
        started_msg = dict(kind="tm", hostname=self._hostname, pid=os.getpid())
        logger.debug("publish *-start")
        self._rs.publish(
            f"{self._channel}-start", json.dumps(started_msg, sort_keys=True)
        )
        logger.debug("published *-start")

    def cleanup(self):
        """cleanup - close down the Redis pubsub object.
        """
        self.logger.debug("%s: cleanup", self._hostname)
        self.logger.debug("unsubscribe")
        self._pubsub.unsubscribe()
        self.logger.debug("pubsub close")
        self._pubsub.close()
        if self._tmp_dir is not None:
            shutil.rmtree(self._tmp_dir)
            self._tmp_dir = None

    def _get_data(self):
        """_get_data - fetch and decode the JSON object off the "wire".

        The keys in the JSON object are validated against the expected keys,
        and the value of the 'state' key is validated against the valid
        states.
        """
        data = None
        while not data:
            if not data:
                self.logger.debug("next")
                try:
                    payload = next(self._chan)
                except Exception:
                    self.logger.exception("Error fetch next piece of data")
                else:
                    self.logger.debug("next success")
            try:
                json_str = payload["data"].decode("utf-8")
                data = json.loads(json_str)
            except Exception:
                self.logger.warning("data payload in message not JSON, %r", json_str)
                data = None
            else:
                keys = frozenset(data.keys())
                if keys != self._message_keys:
                    self.logger.warning(
                        "unrecognized keys in data of payload in message, %r", json_str,
                    )
                    data = None
                elif data["state"] not in self._valid_states:
                    self.logger.warning(
                        "unrecognized state in data of payload in message, %r",
                        json_str,
                    )
                    data = None
                elif data["group"] is not None and data["group"] != self._group:
                    self.logger.warning(
                        "unrecognized group in data of payload in message, %r",
                        json_str,
                    )
                    data = None
        return data

    def wait_for_command(self):
        """wait_for_command - wait for the expected data message for the
        expected state

        Reads messages pulled from the wire, ignoring messages for unexpected
        states, returning an (action, data) tuple when an expected state
        transition is encountered, and setting the next expected state
        properly.
        """
        self.logger.debug("%s: wait_for_command %s", self._hostname, self.state)
        data = self._get_data()
        while data["state"] != self.state:
            if data["state"] == "terminate":
                raise Terminate()
            self.logger.info(
                "ignoring unexpected data, %r, expecting state %s", data, self.state
            )
            data = self._get_data()
        state_rec = self._state_trans[self.state]
        action = state_rec["action"]
        self.state = state_rec["next"]
        self.logger.debug("%s: msg - %r", self._hostname, data)
        return action, data

    def _send_client_status(self, status):
        # The published client status message contains three pieces of
        # information:
        #   {
        #     "kind": "ds|tm",
        #     "hostname": "< the host name on which the ds or tm is running >",
        #     "status": "success|< a message to be displayed on error >"
        #   }
        msg = dict(kind="tm", hostname=self._hostname, status=status)
        self.logger.debug("publish tmc")
        try:
            num_present = self._rs.publish(
                "tool-meister-client", json.dumps(msg, sort_keys=True)
            )
        except Exception:
            self.logger.exception("Failed to publish client status message")
            ret_val = 1
        else:
            self.logger.debug("published tmc")
            if num_present != 1:
                self.logger.error(
                    "client status message received by %d subscribers", num_present
                )
                ret_val = 1
            else:
                self.logger.debug("posted client status, %r", status)
                ret_val = 0
        return ret_val

    def start_tools(self, data):
        """start_tools - start all registered tools executing in the background

        The 'state' and 'group' values of the payload have already been
        validated before this "start tools" action is invoked.

        If this Tool Miester instance is running on the same host as the
        controller, we'll use the given "directory" argument directly for
        where tools will store their collected data.  When this Tool Meister
        instance is remote, we'll use a temporary directory off of the
        ${benchmark_run_dir} (self._benchmark_run_dir).
        """
        if self._running_tools or self._directory is not None:
            self.logger.error(
                "INTERNAL ERROR - encountered previously running tools, '%r'",
                self._running_tools,
            )
            return False

        # script_path=`dirname $0`
        # script_name=`basename $0`
        # pbench_bin="`cd ${script_path}/..; /bin/pwd`"
        # action=`echo ${script_name#pbench-} | awk -F- '{print $1}'`
        # dir=${1}; shift (-d|--dir)
        if self._tmp_dir:
            _dir = self._tmp_dir
        else:
            try:
                _dir = Path(data["directory"]).resolve(strict=True)
            except Exception:
                self.logger.exception(
                    "Failed to access provided result directory, %s", data["directory"]
                )
                return False
        _dir = _dir / self._hostname
        try:
            _dir.mkdir()
        except Exception:
            self.logger.exception("Failed to create local result directory, %s", _dir)
            return False
        self._directory = data["directory"]

        # tool_group_dir="$pbench_run/tools-$group"
        # for this_tool_file in `/bin/ls $tool_group_dir`; do
        # 	tool_opts=()
        # 	while read line; do
        # 		tool_opts[$i]="$line"
        # 		((i++))
        # 	done < "$tool_group_dir/$this_tool_file"
        # name="$this_tool_file"
        failures = 0
        for name, tool_opts in sorted(self._tools.items()):
            try:
                tool = Tool(
                    name, self._group, tool_opts, self.pbench_bin, _dir, self.logger
                )
                tool.start()
            except Exception:
                self.logger.exception(
                    "Failed to start tool %s running in background", name
                )
                failures += 1
                continue
            else:
                self._running_tools[name] = tool
        self._send_client_status("success")
        return failures

    def _wait_for_tools(self):
        failures = 0
        for name in sorted(self._tools.keys()):
            try:
                tool = self._running_tools[name]
            except KeyError:
                self.logger.error(
                    "INTERNAL ERROR - tool %s not found in list of running tools", name,
                )
                failures += 1
                continue
            try:
                tool.wait()
            except Exception:
                self.logger.exception(
                    "Failed to wait for tool %s to stop running in background", name
                )
                failures += 1
        return failures

    def stop_tools(self, data):
        """stop_tools - stop any running tools.

        The 'state' and 'group' values of the payload have already been
        validated before this "stop tools" action is invoked.

        This method only proceeds if the 'directory' entry value of the
        payload matches what was previously provided to a "start tools"
        action.
        """
        if self._directory != data["directory"]:
            self.logger.error(
                "INTERNAL ERROR - stop tools action encountered for a"
                " directory, '%s', that is different from the previous"
                " start tools, '%s'",
                data["directory"],
                self._directory,
            )
            return False

        failures = 0
        for name in sorted(self._tools.keys()):
            try:
                tool = self._running_tools[name]
            except KeyError:
                self.logger.error(
                    "INTERNAL ERROR - tool %s not found in list of running" " tools",
                    name,
                )
                failures += 1
                continue
            try:
                tool.stop()
            except Exception:
                self.logger.exception(
                    "Failed to stop tool %s running in background", name
                )
                failures += 1
        failures += self._wait_for_tools()

        self._send_client_status(
            "success" if failures == 0 else "failures stopping tools"
        )
        return failures

    def send_tools(self, data):
        """send_tools - post-process and send any collected tool data to the
        tool data sink.

        The 'state' and 'group' values of the payload have already been
        validated before this "send tools" action is invoked.

        This method only proceeds if the 'directory' entry value of the
        payload matches what was previously provided to a "start tools"
        action.
        """
        if self._directory != data["directory"]:
            self.logger.error(
                "INTERNAL ERROR - send tools action encountered for a"
                " directory, '%s', that is different from the previous"
                " start tools, '%s'",
                data["directory"],
                self._directory,
            )
            return False

        failures = 0
        for name in sorted(self._tools.keys()):
            try:
                tool = self._running_tools[name]
            except KeyError:
                self.logger.error(
                    "INTERNAL ERROR - tool %s not found in list of running" " tools",
                    name,
                )
                failures += 1
                continue
            try:
                tool.postprocess()
            except Exception:
                self.logger.exception("Failed to post-process tool %s data", name)
                failures += 1
        failures += self._wait_for_tools()
        for name in sorted(self._tools.keys()):
            try:
                del self._running_tools[name]
            except KeyError:
                self.logger.error(
                    "INTERNAL ERROR - tool %s not found in list of running" " tools",
                    name,
                )
                failures += 1
                continue

        if self._hostname == self._controller:
            self.logger.info(
                "%s: send_tools (no-op) %s %s",
                self._hostname,
                self._group,
                self._directory,
            )
        else:
            tar_file = self._tmp_dir / f"{self._hostname}.tar.xz"
            o_file = self._tmp_dir / f"{self._hostname}.tar.out"
            e_file = self._tmp_dir / f"{self._hostname}.tar.err"
            try:
                # Invoke tar directly for efficiency.
                with o_file.open("w") as ofp, e_file.open("w") as efp:
                    cp = subprocess.run(
                        ["/usr/bin/tar", "-Jcf", tar_file, self._hostname],
                        cwd=self._tmp_dir,
                        stdin=None,
                        stdout=ofp,
                        stderr=efp,
                    )
            except Exception:
                self.logger.exception("Failed to create tools tar ball '{}'", tar_file)
            else:
                if cp.returncode != 0:
                    self.logger.error(
                        "Failed to create tools tar ball; return code: %d",
                        cp.returncode,
                    )
                    failures += 1
                else:
                    try:
                        tar_md5 = md5sum(tar_file)
                    except Exception:
                        self.logger.exception("Failed to read tools tar ball")
                        failures += 1
                    else:
                        self.logger.info(
                            "%s: send_tools %s %s",
                            self._hostname,
                            self._group,
                            self._directory,
                        )
                        headers = {"md5sum": tar_md5}
                        directory_bytes = data["directory"].encode("utf-8")
                        tool_data_ctx = hashlib.md5(directory_bytes).hexdigest()
                        url = f"http://{self._controller}:8080/tool-data/{tool_data_ctx}/{self._hostname}"
                        sent = False
                        retries = 200
                        while not sent:
                            try:
                                with tar_file.open("rb") as tar_fp:
                                    response = requests.put(
                                        url, headers=headers, data=tar_fp
                                    )
                            except (
                                ConnectionRefusedError,
                                requests.exceptions.ConnectionError,
                            ) as exc:
                                self.logger.debug("%s", exc)
                                # Try until we get a connection.
                                time.sleep(0.1)
                                retries -= 1
                                if retries <= 0:
                                    raise
                            else:
                                sent = True
                                if response.status_code != 200:
                                    self.logger.error(
                                        "PUT '%s' failed with '%d', '%s'",
                                        url,
                                        response.status_code,
                                        response.text,
                                    )
                                    failures += 1
                                else:
                                    self.logger.debug(
                                        "PUT '%s' succeeded ('%d', '%s')",
                                        url,
                                        response.status_code,
                                        response.text,
                                    )
                                    try:
                                        shutil.rmtree(self._tmp_dir / self._hostname)
                                    except Exception:
                                        self.logger.exception(
                                            "Failed to remove tool data hierarchy, '%s'",
                                            self._tmp_dir / self._hostname,
                                        )
                                        failures += 1
                        self.logger.debug(
                            "%s: send_tools completed",
                            self._hostname,
                            self._group,
                            self._directory,
                        )
            finally:
                try:
                    tar_file.unlink()
                except Exception:
                    self.logger.warning(
                        "failed to remove tools tar ball, '%s'", tar_file
                    )
        self._directory = None

        self._send_client_status(
            "success" if failures == 0 else "failures sending tool data"
        )
        return failures
