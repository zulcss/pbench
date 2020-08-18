from pathlib import Path


class TriggerListMixin:
    def list(self):
        if not self.context.group:
            self.context.group = self.groups
            for group in self.context.group:
                tg_dir = Path(self.tools_group_dir(group), "__trigger__")
                if tg_dir.exists():
                    print("%s: %s" % (group, tg_dir.read_text().strip()))
        else:
            if self.context.group not in self.groups:
                self.logger.error("bad group specified")
                return 1
            tg_dir = Path(self.tools_group_dir(self.context.group), "__trigger__")
            if tg_dir.exists():
                print("%s: %s" % (group, tg_dir.read_text().strip()))
