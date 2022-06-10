from discord.errors import CheckFailure


class CommandDisabledError(CheckFailure):
    """Raised when a command is disabled."""

    def __init__(self, command):
        self.command = command
