import json
from typing import Optional, Generator

import httpx
from snowleopard.client_base import SLClientBase
from snowleopard.models import parse, RetrieveResponseObjects, ResponseDataObjects


class SnowLeopardClient(SLClientBase):
    client: httpx.Client

    def __init__(
        self,
        loc: str = None,
        token: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
    ):
        config = self._config(loc, token, timeout)
        self.client = httpx.Client(
            base_url=config.loc,
            headers=config.headers(),
            timeout=config.timeout
        )

    def retrieve(
        self, datafile_id: str, user_query: str
    ) -> RetrieveResponseObjects:
        resp = self.client.post(
            # url=f"/datafiles/{datafile_id}/retrieve",
            url=f"api/self/datafiles/{datafile_id}/proxy/retrieve",
            json={"userQuery": user_query},
        )
        return self._parse_retrieve(resp)

    def response(self, datafile_id: str, user_query: str) -> Generator[ResponseDataObjects, None, None]:
        resp = self.client.post(
            url=f"api/self/datafiles/{datafile_id}/proxy/response",
            json={"userQuery": user_query},
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            yield parse(json.loads(line))

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)

    def close(self):
        self.client.close()
