import configparser
import os
import pathlib
import sys

from pbench.common import configtools
from pbench.common import exception


class AgentConfig:
    def __init__(self, cfg_name=None):
        self.cfg_name = self._get_agent_default_conf(cfg_name)
        config_files = configtools.file_list(self.cfg_name)
        config_files.reverse()
        self.conf = configparser.ConfigParser()
        self.files = self.conf.read(config_files)

    def _get_agent_default_conf(self, cfg_name):
        """Get the default config directory of pbench-agent

        :return: default pbench agent config
        """
        if cfg_name:
            path = pathlib.Path(cfg_name)
            if not path.exists():
                raise exception.MissingConfig("Config not found: {}".format(cfg_name))
        else:
            pbench_cfg = os.environ.get("_PBENCH_AGENT_CONFIG", None)
            if pbench_cfg:
                path = pathlib.Path(pbench_cfg)
                if not path.exists():
                    raise exception.MissingConfig(
                        "Config not found: {}".format(pbench_cfg)
                    )
            else:
                raise exception.BrokenConfig("PBENCH_AGENT_CONFIG is not")

        return str(path)

    def get_pbench_run(self):
        """Get the pbench_agent/pbench_run for agent config"""
        try:
            return self.conf.get("pbench-agent", "pbench_run")
        except configparser.NoOptionError:
            return "/var/lib/pbench-agent"

    def get_pbench_tmp(self):
        """Get the pbench_agent/pbench_run/tmp config"""
        pbench_run = self.get_pbench_run()
        path = pathlib.Path(pbench_run)
        path = path / "tmp"
        path.mkdir()
        if not path.exists():
            print("Unable to create TMP dir. {}".format(str(pbench_run)))
            sys.exit(1)
        return str(path)

    def get_pbench_log(self):
        """Get the pbench_agent/pbench_log agent config"""
        try:
            return "%s/pbench.log" % self.conf.get("pbench-agent", "pbench_log")
        except configparser.NoOptionError:
            return "%s/pbench.log" % self.get_pbench_run()

    def get_pbench_install_dir(self):
        """Get the pbench_agent/install-dir agent config"""
        try:
            install_dir = self.conf.get("pbench-agent", "install-dir")
            path = pathlib.Path(install_dir)
            if not path.exists():
                print(
                    "pbench installation directory {} does not exist".format(
                        install_dir
                    )
                )
                sys.exit(1)
            return install_dir
        except configparser.NoOptionError:
            return "/opt/pbench-agent"

    def get(self, *args, **kwargs):
        return self.conf.get(*args, **kwargs)
