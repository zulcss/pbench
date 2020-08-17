from pathlib import Path

from pbench.agent import base
from pbench.agent.tools.clear import ClearMixin


class ToolBase(base.Base, ClearMixin):
    def __init__(self, context):
        super(ToolBase, self).__init__(context)

        self.tg_dir = self.tools_group_dir(self.context.group)

    def execute(self):
        pass

    def tools_group_dir(self, group):
        return Path(self.pbench_run, f"tools-v1-{group}")

    @property
    def remotes(self):
        try:
            return [
                p.name
                for p in self.tg_dir.iterdir()
                if p.name != "__trigger__" and p.is_dir()
            ]
        except FileNotFoundError:
            self.logger.error("%s is not found", self.tg_dir)
            return []

    def tools(self, dir):
        return [
            p.name
            for p in dir.iterdir()
            if p.name != "__label__" and p.suffix != ".__noinstall__"
        ]
