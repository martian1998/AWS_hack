class DomainError(Exception):
    def __init__(self, status: int, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.status, self.code, self.message, self.retryable = status, code, message, retryable


class Conflict(Exception):
    """Optimistic transaction conflict; retry the complete decision."""


class StorageUnavailable(DomainError):
    def __init__(self):
        super().__init__(503, "STORAGE_UNAVAILABLE", "Work was not confirmed accepted. Retry with the same operation ID.", True)
