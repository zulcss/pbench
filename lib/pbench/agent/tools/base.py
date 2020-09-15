from pbench.agent.base import BaseCommand
from pbench.agent.tools.clear import ClearMixIn
from pbench.agent.tools.list import ListMixIn


class ToolCommand(BaseCommand, ClearMixIn, ListMixIn):
    def __init__(self, context):
        super(ToolCommand, self).__init__(context)

    def tools(self, path):
        return [
            p
            for p in path.iterdir()
            if p.name != "__label__" and p.suffix != ".__noinstall__"
        ]
