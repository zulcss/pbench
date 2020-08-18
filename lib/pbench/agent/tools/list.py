class ListMixin:
    def list(self):
        """List registered tools"""
        if not self.context.group:
            self.context.group = self.groups

        if self.context.name:
            groups = []
            for group in self.context.group:
                for path in self.tools_group_dir(group).iterdir():
                    if path.name == "__trigger__":
                        continue
                    if any(path.iterdir()):
                        if group not in groups:
                            groups.append(group)
            if groups:
                print(
                    "tool name: %s groups: %s" % (self.context.name, ", ".join(groups))
                )
        else:
            dirs = {}
            for group in self.context.group:
                dirs[group] = {}
                for path in self.tools_group_dir(group).iterdir():
                    dirs[group][path.name] = self.tools(path)
            for k, v in dirs.items():
                print("%s: " % k, ", ".join("{} {}".format(h, t) for h, t in v.items()))
