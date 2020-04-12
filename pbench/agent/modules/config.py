import os
import pathlib
import shutil

from pbench.agent.core import config
from pbench.agent.modules import base


class AgentUtilConfig(base.Base):
    def execute(self):
        pbench_config = self.command_args.get("config", None)
        if not pbench_config:
            raise Exception("Configuration file is not specified")
        pbench_run = (
            pathlib.Path(config.AgentConfig(pbench_config).get_install_dir()) / "config"
        )
        pbench_run.mkdir(parents=True, exist_ok=True)
        shutil.copy(pbench_config, pbench_run)


class ConfigSSHKey(base.Base):
    def execute(self):
        pbench_config = self.command_args.get("config", None)
        ssh_key = self.command_args.get("ssh_key", None)

        if not pbench_config:
            raise Exception("Configuration file is not sepcified")
        if not ssh_key:
            raise Exception("SSH key file is not specified")

        c = config.AgentConfig(pbench_config)
        dest = pathlib.Path(c.get_install_dir()) / "id_rsa"
        src = pathlib.Path(ssh_key)
        if src.exists():
            shutil.copy(src, dest)
            os.chmod(str(dest), 600)
