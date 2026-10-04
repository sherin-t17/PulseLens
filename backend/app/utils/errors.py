"""
One custom exception type for every "expected" failure (bad video, too short,
noisy signal, missing measurement...). main.py turns it into a clean JSON
message with the right HTTP status code, so users never see Python stack traces.
"""


class PulseLensError(Exception):
    """An error whose message is safe and understandable to show the user."""

    def __init__(self, message, status_code=422):
        super().__init__(message)
        self.message = message
        self.status_code = status_code