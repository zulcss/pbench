from pathlib import Path


class RegisterMixin:
    def register(self):
        """Register a tool"""
        tg_dir = self.tools_group_dir(self.context.group)
        tg_dir.mkdir(parents=True, exist_ok=True)

        for host in self.context.remotes:
            tg_dir_r = Path(tg_dir, host["remote"])
            tg_dir_r.mkdir(parents=True, exist_ok=True)

            if tg_dir_r.exists():
                tool_file = Path(tg_dir_r, self.context.name)
                tool_file.touch()
                if self.context.tool_opts:
                    tool_file.write_text("\n".join(self.context.tool_opts))
                if self.context.noinstall:
                    tool_install = Path(tg_dir_r, f"{self.context.name}.__noinstall__")
                    if tool_install.exists():
                        tool_install.unlink()
                    Path(tool_install).symlink_to(tool_file)

                label_msg = ""
                if host["label"]:
                    label = Path(tg_dir_r, "__label__")
                    if label.exists():
                        label.unlink()
                    label.write_text("\n".join(host["label"]))
                    label_msg = f', with label "{"".join(host["label"])}"'

                self.logger.info(
                    '"%s" tool is now registered for host "%s"%s in group "%s"',
                    self.context.name,
                    host["remote"],
                    label_msg,
                    self.context.group,
                )

            else:
                self.logger.error("Failed to make %s", tg_dir_r)
