from pathlib import Path


class ToolCli:
    def tools_group_dir(self, group):
        """Generate the pbench_run tool group path.
           Returns a posixpath
        :param group: tool group name
        """
        return Path(self.pbench_run, f"tools-v1-{group}")
