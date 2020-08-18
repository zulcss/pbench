from pbench.agent import base
from pbench.agent.tools.clear import ClearMixin
from pbench.agent.tools.list import ListMixin
from pbench.agent.tools.register import RegisterMixin


class ToolBase(base.Base, ClearMixin, ListMixin, RegisterMixin):
    def __init__(self, context):
        super(ToolBase, self).__init__(context)

        self.tg_dir = self.tools_group_dir(self.context.group)

    def execute(self):
        pass

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

    @property
    def groups(self):
        return [
            path.name.split("tools-v1-")[1]
            for path in self.pbench_run.glob("tools-v1-*")
        ]
