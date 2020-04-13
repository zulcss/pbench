import pathlib

from plumbum import local
from plumbum.path.utils import delete

from pbench.agent.core.config import AgentConfig
from pbench.agent.modules import base


class PbenchCleanup(base.Base):
    def execute(self):
        pbench_dir = AgentConfig().get_pbench_run()
        path = pathlib.Path(pbench_dir)
        print("Cleaning up {}".format(str(pbench_dir)))
        if path.exists():
            with local.cwd(pbench_dir) as f:
                delete(f // "*")


class PbenchClearResults(base.Base):
    def execute(self):
        pbench_dir = AgentConfig().get_pbench_run()
        path = pathlib.Path(pbench_dir)
        if path.exists():
            for file in sorted(path.glob("*"), reverse=True):
                if not (
                    str(file.name).startswith("tools")
                    or str(file.name).startswith("tmp")
                ):
                    if file.is_fil():
                        file.unlink()
                    if file.is_dir():
                        file.rmdir()
