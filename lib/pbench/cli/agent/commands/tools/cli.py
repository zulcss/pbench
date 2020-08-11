import os
from pathlib import Path
import shutil

from pbench.agent.exceptions import Error


class ToolCli:
    def tools_group_dir(self, group):
        """Generate the pbench_run tool group path.
           Returns a posixpath
        :param group: tool group name
        """
        return Path(self.pbench_run, f"tools-v1-{group}")

    def tools(self, path):
        return [
            p.name
            for p in path.iterdir()
            if p.name != "__label__" and p.suffix != ".__noinstall__"
        ]

    @property
    def groups(self):
        return [
            path.name.split("tools-v1-")[1]
            for path in self.pbench_run.glob("tools-v1-*")
        ]

    def remotes(self, group):
        return [
            path.name
            for path in self.tools_group_dir(group).iterdir()
            if path.name != "__trigger__"
        ]

    def clear_tools(self):
        """Clear the registered tools"""
        tg_dir = self.tools_group_dir(self.context.group)
        if not self.context.remotes:
            self.context.remotes = [
                p for p in tg_dir.iterdir() if p.name != "__trigger__"
            ]

        for remote in self.context.remotes:
            if remote.is_file():
                self.logger.warning(
                    'The given remote host, "%s", is not a directory in %s.',
                    remote,
                    tg_dir,
                )
                continue
            if not self.context.name:
                self.context.name = [
                    p
                    for p in remote.iterdir()
                    if p.name != "__label__" and p.suffix != ".__noinstall__"
                ]

            for name in self.context.name:
                tool_file = Path(tg_dir, remote, name)
                if tool_file.exists():
                    try:
                        os.unlink(tool_file)
                        install = Path(f"{tool_file}.__noinstall__")
                        if install.exists():
                            os.unlink(install)
                        label = Path(tg_dir, remote, "__label__")
                        if label.exists():
                            os.unlink(label)
                        self.logger.info(
                            'Removed "%s" from host, "%s", in tools group, "%s"',
                            name,
                            remote.name,
                            self.context.group,
                        )
                    except OSError as ex:
                        raise Error("Failed to remove %s", tool_file)
                        if self.context.debug:
                            self.logger.exception(ex)

                    tg_r = Path(tg_dir, remote)
                    if not any(tg_r.iterdir()):
                        self.logger.info("All tools removed from host, %s", remote.name)
                        try:
                            shutil.rmtree(tg_r)
                        except shutil.Error as ex:
                            raise Error("Failed to remote %s", tg_r)
                            if self.context.debug:
                                self.logger.exception(ex)

    def list_tools(self):
        """List registered tools"""
        self.logger.debug("in list_tools")

        if not self.context.group:
            self.context.group = self.groups

        if self.context.name:
            groups = []
            for group in self.context.group:
                for path in self.tools_group_dir(group).iterdir():
                    if path.name == "__trigger__":
                        continue
                    if any(path.iterdir()):
                        if self.context.name in self.tools(path):
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
                for path in self.tools_group_dir(group).glob("*/**"):
                    dirs[group][path.name] = self.tools(path)
            for k, v in dirs.items():
                print("%s: " % k, ", ".join("{} {}".format(h, t) for h, t in v.items()))

    def register_tool(self):
        self.logger.debug("in register")

        tg_dir = self.tools_group_dir(self.context.group)
        tg_dir.mkdir(parents=True, exist_ok=True)

        for host in self.context.remotes["remotes"]:
            tg_dir_r = Path(tg_dir, host)
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
                if self.context.remotes["labels"]:
                    label = Path(tg_dir_r, "__label__")
                    if label.exists():
                        label.unlink()
                    label.write_text("\n".join(self.context.remotes["labels"]))
                    label_msg = (
                        f', with label "{"".join(self.context.remotes["labels"])}"'
                    )

                self.logger.info(
                    '"%s" tool is now registered for host "%s"%s in group "%s"',
                    self.context.name,
                    host,
                    label_msg,
                    self.context.group,
                )

            else:
                self.logger.error("Failed to make %s", tg_dir_r)
