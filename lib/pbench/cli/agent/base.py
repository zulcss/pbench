class Base:
    """An base class used to define the command interface."""

    def __init__(self, context):
        self.context = context

    def execute(self):
        """Execute the required command"""
        pass
