import configparser
import os
import pathlib

from pbench.agent.core.utils import normalize_path, sysexit
from pbench.common import configtools


class AgentConfig(object):
    def __init__(self, config_file=None):
        self.config_file = config_file
        if not self.config_file:
            self.config = self._get_agent_config()
        config_files = configtools.file_list(self.config)
        config_files.reverse()
        self.conf = configparser.ConfigParser()
        self.files = self.conf.read(config_files)

    def _get_agent_config(self):
        """Get the agent configuration file from the ENV. Raise an exception
           if the file does not exist or the envrionment is not setup correctly
           :return: path of agent config file
        """
        pbench_cfg = os.path.abspath(os.environ.get("_PBENCH_AGENT_CONFIG", None))
        if pbench_cfg:
            path = pathlib.Path(pbench_cfg)
            """ Make sure that the config exists and its a file"""
            if not path.exists():
                raise Exception("Config not found: {}".format(pbench_cfg))
            if not path.is_file():
                raise Exception(
                    "Not a valid configuration file: " "{}".format(pbench_cfg)
                )

            """"Make sure that the config file is valid"""
            try:
                configparser.ConfigParser().read(pbench_cfg)
            except configparser.Error as e:
                print(e)
                sysexit(2)
        else:
            raise Exception("PBENCH_AGENT_CONFIG is not set")

        return normalize_path(path)

    def get_pbench_run(self):
        """Determine the agent run directory"""
        try:
            path = self.conf.get("pbench-agent", "pbench_run")
            if not pathlib.Path(path).exists():
                raise Exception(
                    "The provided pbench run directory: {}, "
                    "does not exist".format(path)
                )
                sysexit(1)
            return path
        except configparser.Error:
            return "/var/lib/pbench-agent"

    def get_pbench_tmp(self):
        """Determine the agent tmp directory"""
        pbench_tmp = pathlib.Path(self.get_pbench_run()) / "tmp"
        pbench_tmp.mkdir()
        if not pbench_tmp.exists():
            raise Exception("Unable to create TMP dir, " "{}".format(str(pbench_tmp)))
        return normalize_path(pbench_tmp)

    def get_pbench_log(self):
        """Determine the agent log file"""
        try:
            pbench_log = pathlib.Path(self.conf.get("pbench-agent", "pbench_log"))
            return normalize_path(pbench_log) + "/pbench.log"
        except configparser.Error:
            return "/var/lib/pbench-agent/pbench.log"

    def get_install_dir(self):
        """Determine the agene install dir"""
        try:
            pbench_install_dir = pathlib.Path(
                self.conf.get("pbench-agent", "install-dir")
            )
            if not pbench_install_dir.exists():
                raise Exception(
                    "pbench installation directory, {} "
                    "does not exist".format(str(pbench_install_dir))
                )
            return normalize_path(pbench_install_dir)
        except configparser.Error:
            return "/opt/pbench-agent"

    def get_pbench_pbspp_dir(self):
        return os.path.join(self.get_install_dir(), "bench-scripts/postprocess")

    def get_pbench_lib_dir(self):
        return os.path.join(self.get_install_dir(), "lib")

    def get(self, *args, **kwargs):
        return self.conf.get(*args, **kwargs)
