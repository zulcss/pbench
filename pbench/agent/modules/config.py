import configparser
import os
import pathlib
import pwd
import shutil

from pbench.agent.config import AgentConfig


class PbenchToolConfig(object):
    def __init__(self, command_args):
        self.command_args = command_args
        self.cfg_name = None
        if "cfg_file" in self.command_args:
            self.cfg_name = self.command_args["cfg_file"]
        self.config = AgentConfig(self.cfg_name)

    def config_activate(self):
        config_file = self.command_args["cfg_file"]
        src = pathlib.Path(config_file)
        if not src.exists():
            print("{} does not exist".format(str(config_file)))

        pbench_install_dir = pathlib.Path(self.config.get_pbench_install_dir())

        dest = pbench_install_dir / "config"
        dest.mkdir(exist_ok=True)
        shutil.copy(src, dest)

    def config_ssh_key(self):
        keyfile = self.command_args["keyfile"]

        try:
            user = self.config.get("pbench-agent", "pbench_user")
            group = self.config.get("pbench-agent", "pbench_group")
        except (configparser.NoOptionError, configparser.NoSectionError):
            user = "pbench"
            group = "pbench"

        user = pwd.getpwnam(user).pw_uid
        group = pwd.getpwnam(group).pw_gid

        pbench_dir = self.config.get_pbench_install_dir()
        pbench_path = pathlib.Path(pbench_dir)
        keyfile_path = pathlib.Path(keyfile)
        pbench_keyfile = pbench_path / "id_rsa"
        if keyfile_path.exists():
            shutil.copy(str(keyfile_path), str(pbench_keyfile))
            os.chmod(str(pbench_keyfile), 600)
