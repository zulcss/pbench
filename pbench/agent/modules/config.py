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
