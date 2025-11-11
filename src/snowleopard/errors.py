import httpx


class SLError(Exception):
    pass


class APIError(SLError):
    response: httpx.Response

    def __init__(self, description, response: httpx.Response):
        super().__init__(description)
        self.response = response


class StatusError(SLError):
    status: str

    def __init__(self, message, status):
        super().__init__(message)
        self.status = status
