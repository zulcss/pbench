import pathlib
import shutil
import sys

from plumbum import local

from pbench.agent.config import AgentConfig

class PbenchCleanup(object):
    def __init__(self, command_args={}):
        self.command_args = command_args
        self.config = AgentConfig()
    
    def cleanup(self):
        pbench_run_dir = self.config.get_pbench_run()
        for d in local.path(pbench_run_dir):
            path = pathlib.Path(d)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    
    def clear_results(self):
        path = pathlib.Path(
            self.config.get_pbench_run())
        for p in path.rglob('*'):
            if p.stem.startswith('tmp') or p.stem.startswith('tools'):
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(str(p))
    
    def clear_tools(self):
        pbench_run_dir = pathlib.Path(
            self.config.get_pbench_run())
        if not pbench_run_dir.exists():
            sys.exit(1)

        group = self.command_args.get("group", None)
        tool = self.command_args.get("tool", "*")

        regex = "tools-"
        if group:
            regex = regex + group + "/*"
        else:
            regex = regex + "default/*"
        
        for file in pbench_run_dir.rglob(regex):
            if file.match(tool):
                if file.is_file():
                    file.unlink()