import errno
import os
import time
import subprocess

from pathlib import Path


class ToolException(Exception):
    pass


class Tool(object):
    """Encapsulates all the state needed to manage a tool running as a background
    process.

    The ToolMeister class uses one Tool object per running tool.

    FIXME: this class effecitvely re-implements the former
    "tool-scripts/base-tool" bash script.
    """

    def __init__(self, name, group, tool_opts, pbench_bin, tool_dir, logger):
        self.logger = logger
        self.name = name
        self.group = group
        self.tool_opts = tool_opts
        self.pbench_bin = pbench_bin
        self.tool_dir = tool_dir
        self.screen_name = f"pbench-tool-{group}-{name}"
        self.start_process = None
        self.stop_process = None
        self.post_process = None

    def _check_no_processes(self):
        if self.start_process is not None:
            raise ToolException(
                f"Tool({self.name}) has an unexpected start process running"
            )
        if self.stop_process is not None:
            raise ToolException(
                f"Tool({self.name}) has an unexpected stop process running"
            )
        if self.post_process is not None:
            raise ToolException(
                f"Tool({self.name}) has an unexpected post-process process running"
            )

    def start(self):
        """Creates the background `screen` process running the tool's "start"
        operation.
        """
        self._check_no_processes()
        # screen -dm -L -S \"${screen_name}\" ${pbench_bin}/tool-scripts/${name} --${action} --dir=${tool_output_dir} ${tool_opts[@]}
        args = [
            "/usr/bin/screen",
            "-dmS",
            self.screen_name,
            f"{self.pbench_bin}/tool-scripts/{self.name}",
            "--start",
            f"--dir={self.tool_dir}",
            self.tool_opts,
        ]
        self.logger.info("%s: start_tool -- %s", self.name, " ".join(args))
        self.start_process = subprocess.Popen(args)

    def stop(self):
        """Creates the background `screen` process to running the tool's "stop"
        operation.
        """
        if self.start_process is None:
            raise ToolException(f"Tool({self.name})'s start process not running")
        if self.stop_process is not None:
            raise ToolException(
                f"Tool({self.name}) has an unexpected stop process running"
            )
        if self.post_process is not None:
            raise ToolException(
                f"Tool({self.name}) has an unexpected post-process process running"
            )

        # FIXME - before we "stop" a tool, check to see if a
        # "{tool}/{tool}.pid" file exists.  If it doesn't wait for a second to
        # show up, if after a second it does not show up, then give up waiting
        # and just call the stop method.
        tool_pid_file = self.tool_dir / self.name / f"{self.name}.pid"
        cnt = 0
        while not tool_pid_file.exists() and cnt < 100:
            time.sleep(0.1)
            cnt += 1
        if not tool_pid_file.exists():
            self.logger.warning(
                "Tool(%s) pid file, %s, does not exist after waiting 10 seconds",
                self.name,
                tool_pid_file,
            )

        # $pbench_bin/tool-scripts/$name --$action --dir=${tool_output_dir} "${tool_opts[@]}"
        args = [
            f"{self.pbench_bin}/tool-scripts/{self.name}",
            "--stop",
            f"--dir={self.tool_dir}",
            self.tool_opts,
        ]
        self.logger.info("%s: stop_tool -- %s", self.name, " ".join(args))
        o_file = self.tool_dir / f"tm-{self.name}-stop.out"
        e_file = self.tool_dir / f"tm-{self.name}-stop.err"
        with o_file.open("w") as ofp, e_file.open("w") as efp:
            self.stop_process = subprocess.Popen(
                args, stdin=None, stdout=ofp, stderr=efp
            )

    def wait(self):
        """Wait for any tool processes to terminate after a "stop" process has
        completed.

        Waits for the tool's "stop" process to complete, if started, then
        waits for the tool's start process to complete. Finally, if there is a
        post-processing process running, wait for that to complete before
        returning.
        """
        if self.stop_process is not None:
            if self.start_process is None:
                raise ToolException(
                    f"Tool({self.name}) does not have a start process running"
                )
            if self.post_process is not None:
                raise ToolException(
                    f"Tool({self.name}) has an unexpected post-process process running"
                )
            self.logger.info("waiting for stop %s", self.name)
            # We wait for the stop process to finish first ...
            self.stop_process.wait()
            self.stop_process = None
            # ... then we wait for the start process to finish
            self.start_process.wait()
            self.start_process = None
        elif self.post_process is not None:
            if self.start_process is not None:
                raise ToolException(
                    f"Tool({self.name}) has an unexpected start process running"
                )
            if self.stop_process is not None:
                raise ToolException(
                    f"Tool({self.name}) has unexpected stop process running"
                )
            self.logger.info("waiting for post-process %s", self.name)
            self.post_process.wait()
            self.post_process = None
        else:
            raise ToolException(
                f"Tool({self.name}) wait not called after 'stop' or 'post-process'"
            )

    def postprocess(self):
        """Run the tool's "post-process" action in the background.
        """
        self._check_no_processes()
        # $pbench_bin/tool-scripts/$name --postprocess --dir=$dir "${tool_opts[@]}"
        args = [
            f"{self.pbench_bin}/tool-scripts/{self.name}",
            "--postprocess",
            f"--dir={self.tool_dir}",
            self.tool_opts,
        ]
        self.logger.info("%s: post-process_tool -- %s", self.name, " ".join(args))
        o_file = self.tool_dir / f"tm-{self.name}-postprocess.out"
        e_file = self.tool_dir / f"tm-{self.name}-postprocess.err"
        with o_file.open("w") as ofp, e_file.open("w") as efp:
            self.post_process = subprocess.Popen(
                args, stdin=None, stdout=ofp, stderr=efp
            )


class ToolGroup(object):
    tg_prefix = "tools-v1"

    def __init__(self, group):
        self.group = group
        _pbench_run = os.environ["pbench_run"]
        self.tg_dir = Path(_pbench_run, f"{self.tg_prefix}-{self.group}").resolve(
            strict=True
        )
        if not self.tg_dir.is_dir():
            raise Exception(
                f"bad tool group, {group}: directory {self.tg_dir} does not exist"
            )

        # __trigger__
        try:
            with (self.tg_dir / "__trigger__").open("r") as fp:
                _trigger = fp.read()
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise
            # Ignore missing trigger file
            self.trigger = None
        else:
            if len(_trigger) == 0:
                # Ignore empty trigger file contents
                self.trigger = None
            else:
                self.trigger = _trigger

        # toolnames - Dict with tool name as the key, dictionary with host
        # names and parameters for each host
        self.toolnames = {}
        # hostnames - Dict with host name as the key, dictionary with tool
        # names and parameters for each tool
        self.hostnames = {}
        self.labels = {}
        for hdirent in os.listdir(self.tg_dir):
            if hdirent == "__trigger__":
                # Ignore handled above
                continue
            if not (self.tg_dir / hdirent).is_dir():
                # Ignore wayward non-directory files
                continue
            # We assume this directory is a hostname.
            host = hdirent
            if host not in self.hostnames:
                self.hostnames[host] = {}
            for tdirent in os.listdir(self.tg_dir / host):
                if tdirent == "__label__":
                    with (self.tg_dir / host / tdirent).open("r") as fp:
                        self.labels[host] = fp.read()
                    continue
                if tdirent.endswith("__noinstall__"):
                    # FIXME: ignore "noinstall" for now, tools are going to be
                    # in containers so this does not make sense going forward.
                    continue
                tool = tdirent
                with (self.tg_dir / host / tool).open("r") as fp:
                    tool_opts = fp.read()
                if tool not in self.toolnames:
                    self.toolnames[tool] = {}
                self.toolnames[tool][host] = tool_opts

    def get_tools(self, host):
        """Given a target host, return a dictionary with the list of tool names
        as keys, and the values being their options for that host.
        """
        tools = dict()
        for tool, opts in self.toolnames.items():
            try:
                host_opts = opts[host]
            except KeyError:
                # This host does not have this tool registered, ignore.
                pass
            else:
                tools[tool] = host_opts
        return tools
