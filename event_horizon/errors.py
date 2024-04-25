class InvalidPasswordException(ValueError):
    def __init__(self, message):
        super().__init__(f"password must {message}")
