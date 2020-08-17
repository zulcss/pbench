import os
import shutil
from pathlib import Path


class ClearMixin:
    def clear(self):
        """Clear the registered tools."""
        if not self.context.remotes:
            self.context.remotes = self.remotes

        if len(self.context.remotes) == 0:
            # No remotes are found so exit
            return 1

        for remote in self.context.remotes:
            if not self.context.name:
                self.context.name = self.tools((self.tg_dir / remote))
            for name in self.context.name:
                tool_file = Path(self.tg_dir, remote, name)
                if tool_file.exists():
                    # Remove tool file
                    self._remove(tool_file)

                    # Remove label
                    self._remove(Path(self.tg_dir, remote, "__label__"))

                    # Remove noinstall
                    self._remove(Path(f"{tool_file}.__noinstall__"))

                    self.logger.info(
                        'Removed "%s" from host, "%s", in tools group, "%s"',
                        name,
                        remote,
                        self.context.group,
                    )
            tg_r = Path(self.tg_dir, remote)
            if not any(tg_r.iterdir()):
                self.logger.info("All tools removed from host, %s", remote)
                try:
                    shutil.rmtree(tg_r)
                except shutil.Error as ex:
                    self.logger.exception("Failed to remote %s: %s", tg_r, ex)

    def _remove(self, path):
        """Safe deletion of a file"""
        if path.exists():
            try:
                os.unlink(path)
            except OSError as ex:
                self.logger.error("Failed to delete %s: %s", path, ex)
