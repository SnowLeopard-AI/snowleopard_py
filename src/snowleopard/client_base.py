# -*- coding: utf-8 -*-
# copyright 2025 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import httpx
from snowleopard.models import parse


@dataclass
class SLConfig:
    loc: str
    token: str
    timeout: httpx.Timeout

    def headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

class SLClientBase:
    @staticmethod
    def _config(loc: Optional[str], token: Optional[str], timeout: Optional[httpx.Timeout]) -> SLConfig:
        loc = loc or os.environ.get("SNOWLEOPARD_LOC", "https://api.snowleopard.ai")
        if not loc:
            raise ValueError(
                'Missing required argument "loc" and envar "SNOWLEOPARD_LOC" not set'
            )
        token = token or os.environ.get("SNOWLEOPARD_API_KEY")
        if token is None:
            raise ValueError(
                'Missing required argument "token" and envar "SNOWLEOPARD_API_KEY" not set'
            )

        timeout = timeout or httpx.Timeout(connect=5.0, read=600.0, write=10.0, pool=5.0)
        return SLConfig(loc, token, timeout)

    @staticmethod
    def _build_path(datafile_id: str, endpoint: str) -> str:
        return f"datafiles/{datafile_id}/{endpoint}"

    @staticmethod
    def _parse_retrieve(resp):
        try:
            return parse(resp.json())
        except Exception:
            resp.raise_for_status()
            raise
