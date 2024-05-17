class InvalidPasswordError(ValueError):
    def __init__(self, message):
        super().__init__(f"password must {message}")


class FailedOperationError(RuntimeError):
    def __init__(self, message):
        super().__init__(f"operation failed: {message}")
