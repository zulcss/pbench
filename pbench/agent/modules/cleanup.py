import pathlib
import sys

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


class PbenchClearTools(base.Base):
    def execute(self):
        pbench_run_dir = pathlib.Path(AgentConfig().get_pbench_run())
        if not pbench_run_dir.exists():
            sys.exit(1)

        group = self.command_args.get("group", None)
        tool = self.command_args.get("tool", None)

        regex = "tools-"
        if group:
            regex = regex + group + "/*"
        else:
            regex = regex + "default/*"

        if tool is None:
            tool = "*"

        for file in pbench_run_dir.rglob(regex):
            if file.match(tool) and file.is_file():
                file.unlink()
