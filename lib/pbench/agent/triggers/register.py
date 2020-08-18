from pathlib import Path


class TriggerRegisterMixIn:
    def register(self):
        trigger = Path(self.tools_group_dir(self.context.group), "__trigger__")
        if trigger.exists():
            trigger.unlink()
        trigger.write_text("%s:%s\n" % (self.context.start, self.context.stop))
        return 0
