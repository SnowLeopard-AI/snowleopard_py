# -*- coding: utf-8 -*-
# copyright 2026 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

import httpx

class SLException(Exception):
    pass


class APIBadRequest(SLException):
    """Raised when the request is invalid due to bad input.

    This is raised for client-side validation errors, such as an empty or
    whitespace-only query string.
    """


class SnowLeopardHTTPError(SLException):
    """Raised when the SnowLeopard API returns an unexpected HTTP error status."""

    status_code: int
    response: httpx.Response

    def __init__(self, status_code: int, response: httpx.Response):
        self.status_code = status_code
        self.response = response
        try:
            body = response.text[:500]
        except Exception:
            body = "<response body unavailable>"
        super().__init__(f"SnowLeopard API error (HTTP {status_code}): {body}")
