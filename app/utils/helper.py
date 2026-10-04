class AiErrorHnadeler(Exception):
    """Custom exception class for handling AI-related errors."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"AiErrorHnadeler: {self.message}"
