from pbench.agent import base
from pbench.agent.triggers.list import TriggerListMixin
from pbench.agent.triggers.register import TriggerRegisterMixIn


class TriggerBase(base.Base, TriggerListMixin, TriggerRegisterMixIn):
    def __init__(self, context):
        super(TriggerBase, self).__init__(context)

        self.tg_dir = self.tools_group_dir(self.context.group)

    def execute(self):
        pass

    @property
    def groups(self):
        return [
            path.name.split("tools-v1-")[1]
            for path in self.pbench_run.glob("tools-v1-*")
        ]
