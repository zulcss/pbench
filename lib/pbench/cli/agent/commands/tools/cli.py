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

    def tools(self, group, remote):
        tools_dir = Path(self.tools_group_dir(group), remote)
        if not tools_dir.exists():
            raise Error("%s does not exist", tools_dir)
        return [
            p.name
            for p in tools_dir.glob("*")
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
