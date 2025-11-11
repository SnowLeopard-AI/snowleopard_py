import httpx


class SLError(Exception):
    pass


class APIError(SLError):
    response: httpx.Response

    def __init__(self, description, response: httpx.Response):
        super().__init__(description)
        self.response = response


class NotInSchema(SLError):
    pass
