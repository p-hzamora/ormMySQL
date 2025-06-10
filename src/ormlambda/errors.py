class CompileError(Exception):
    """Exception raised for errors in the compilation process."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"CompileError: {self.message}"


class NoSuchModuleError(Exception):
    """Raised when a dynamically-loaded module (usually a database dialect)
    of a particular name cannot be located."""

    def __str__(self):
        return f"NoSuchModuleError: {self.args[0]}"
