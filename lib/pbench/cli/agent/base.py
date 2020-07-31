import abc
import datetime
import os
from pathlib import Path
import socket
import sys


import click


class Base(metaclass=abc.ABCMeta):
    """An base class used to define the command interface."""

    def __init__(self, context):
        context.initialize()

        self.context = context
        self.config = self.context.config
        self.debug = self.context.debug

        # very first thing to do is figure out which pbench we are
        self.pbench_run = Path(os.environ.get("pbench_run", self.config.pbench_run))
        if not self.pbench_run.exists():
            click.secho(
                f"[ERROR] the provided pbench run directory, {self.pbench_run}, does not exist",
                err="red",
            )
            sys.exit(1)

        # the pbench temporary directory is always relative to the $pbench_run
        # directory
        self.pbench_tmp = Path(os.environ.get("pbench_tmp", self.config.pbench_tmp))
        self.pbench_tmp.mkdir(parents=True, exist_ok=True)
        if not self.pbench_tmp.exists():
            click.secho(
                f"[ERROR] unable to create TMP dir, {self.pbench_tmp}", err="red"
            )
            sys.exit(1)
        self.pbench_log = Path(os.environ.get("pbench_log", self.config.pbench_log))
        self.pbench_install_dir = Path(
            os.environ.get("pbench_install_dir", self.config.pbench_install_dir)
        )
        if not self.pbench_install_dir.exists():
            click.secho(
                f"[ERROR] pbench installation directory, {self.pbench_install_dir}, does not exist",
                err="red",
            )
            sys.exit(1)
        self.pbench_bspp_dir = os.environ.get(
            "pbench_bspp_dir", (self.pbench_install_dir / "bench-scripts/postprocess")
        )
        self.pbench_lib_dir = Path(
            os.environ.get("pbench_lib_dir", self.config.pbench_lib_dir)
        )

        self.ssh_opts = self.config.ssh_opts
        os.environ["ssh_opts"] = self.ssh_opts

        self.scp_opts = self.config.scp_opts
        os.environ["scp_opts"] = self.scp_opts

        os.environ["_pbench_debug_mode"] = "0"
        if os.environ.get("_PBENCH_UNIT_TESTS"):
            self.date = "1900-01-01T00:00:00"
            self.date_suffix = "1900.01.01T00.00.00"
            self.hostname = "testhost"
            self.full_hostname = "testhost.example.com"
        else:
            self.date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%s")
            self.date_suffix = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H.%M.%s")
            self.hostname = socket.gethostname()
            self.full_hostname = socket.getfqdn()

        pbench_env = {
            "date": self.date,
            "date_suffix": self.date_suffix,
            "hostname": self.hostname,
            "full_hostname": self.full_hostname,
        }
        for k, v in pbench_env.items():
            os.environ[k] = v

    @abc.abstractmethod
    def execute(self):
        """Execute the required command"""
        pass
