import abc


class Base(object, metaclass=abc.ABCMeta):
    def __init__(self, command_args={}):
        self.command_args = command_args
        self._setup()

    def _setup(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass
