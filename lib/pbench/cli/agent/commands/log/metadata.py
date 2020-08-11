from configparser import ConfigParser
import os
from pathlib import Path
import shutil
import sys

import click
import pbr.version

from pbench.agent.utils import setup_logging
from pbench.agent import tool
from pbench.cli.agent import base
from pbench.cli.agent import context
from pbench.cli.agent import options


class Metadata(base.Base, tool.ToolBase):
    def execute(self):
        self.logger = setup_logging(debug=self.context.debug, logfile=self.pbench_log)

        self.logger.debug("context: %s", vars(self.context))

        if self.context.group not in self.groups:
            self.logger.error("invalid tool group specified: %s", self.context.group)
            return 1

        self.benchmark = os.environ.get("benchmark")
        if not self.benchmark:
            self.logger.error("Missing required $benchmark environment variable")
            return 3
        self.date = os.environ.get("date")
        if not self.date:
            self.logger.error("Missing required $date environment variable")
            return 3
        self.full_hostname = os.environ.get("full_hostname")
        if not self.full_hostname:
            self.logger.error("Missing required $full_hostname environment variable")
            return 3
        self.hostname = os.environ.get("hostname")
        if not self.hostname:
            self.logger.error("Missing required $hostname environment variable")
            return 3

        self.tmpdir = Path(self.pbench_tmp, f"pmdlog.{os.getpid()}")

        m_dict = {
            "start": self.metadata_log_start,
            "stop": self.metadata_log_end,
            "int": self.metadata_log_end,
        }

        try:
            m_dict[self.context.args]()
        except KeyError:
            return 2

        return 0

    def metadata_log_start(self):
        # Opportunistically capture the caller's SSH configuration in case they
        # have host specific configurations they might want to consider in the
        # future when reviewing historical data.  The host names used in the
        # config file might be very different from what tools capture in their
        # output.

        ssh_config = Path.home() / ".ssh/config"
        if ssh_config.exists():
            shutil.copy(ssh_config, self.context.dir)
        ssh_config = Path("/etc/ssh/ssh_config")
        if ssh_config.exists():
            shutil.copy(ssh_config, self.context.dir)
        ssh_config = Path("/etc/ssh/ssh_config.d")
        if ssh_config.exists():
            shutil.copytree(ssh_config, (self.context.dir / "ssh"))

        log = Path(self.context.dir, "metadata.log")
        c = open(log, "w")
        config = ConfigParser()

        config.add_section("pbench")
        config.set("pbench", "name", self.context.dir.name)
        config.set("pbench", "script", self.benchmark)
        config.set("pbench", "config", self.config.pbench_conf)
        config.set("pbench", "date", self.date)
        config.set("pbench", "rpm-version", str(pbr.version.VersionInfo("pbench")))

        config.add_section("run")
        config.set("run", "controller", self.full_hostname)
        config.set("run", "ts", self.timestamp)

        config.add_section("tools")
        config.set("tools", "hosts", " ".join(self.remotes(self.context.group)))
        config.set("tools", "group", self.context.group)

        trigger = Path(self.tools_group_dir(self.context.group), "__trigger__")
        config.set("tools", "trigger", trigger.read_text() or "")

        config.add_section(f"tools/{self.full_hostname}")
        config.set(f"tools/{self.full_hostname}", "hostname-s", self.full_hostname)
        for t in self._tool:
            config.set(
                f"tools/{self.full_hostname}", t.name, str(t.read_text() or None)
            )

        config.write(c)
        c.close()

    def metadata_log_end(self):
        log = Path(self.context.dir, "metadata.log")
        if not log.exists():
            self.metadata_log_start()

        config = ConfigParser()
        config.read(log)
        config.set("run", "end_run", self.timestamp)

        iteration = Path(self.context.dir, ".iterations")
        if iteration.exists():
            config.set("pbench", "iterations", iteration.read_text())

        if self.context.args == "int":
            config.set("run", "interruppted", "True")

        c = open(log, "w")
        config.write(c)

    @property
    def _tool(self):
        return [
            p
            for p in self.tools_group_dir(self.context.group).glob("*/*")
            if p.name != "__label__" and p.suffix != ".__noinstall__"
        ]


def _group_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.group = value
        return value

    return click.option(
        "-g",
        "--groups",
        "--group",
        default="default",
        expose_value=False,
        callback=callback,
        required=True,
    )(f)


def _dir_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        _dir = Path(value)
        if not _dir.exists():
            _dir.mkdir(parents=True, exist_ok=True)
        clictxt.dir = _dir
        return value

    return click.option(
        "-d", "--dir", expose_value=False, callback=callback, required=True,
    )(f)


def _args_option(f):
    def callback(ctxt, param, value):
        clictxt = ctxt.ensure_object(context.CliContext)
        clictxt.args = value
        return value

    return click.argument(
        "args_opts", expose_value=False, callback=callback, required=False,
    )(f)


@click.command()
@options.common_options
@_group_option
@_dir_option
@_args_option
@context.pass_cli_context
def metadata(ctxt):
    status = Metadata(ctxt).execute()
    sys.exit(status)
