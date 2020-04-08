import pathlib

from plumbum import local

from pbench.agent.config import AgentConfig

class PbenchCleanup(object):
    def __init__(self):
        self.config = AgentConfig()
    
    def cleanup(self):
        pbench_run_dir = self.config.get_pbench_run()
        for d in local.path(pbench_run_dir):
            path = pathlib.Path(d)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
