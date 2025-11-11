import json
from typing import AsyncGenerator, Optional

import httpx
from snowleopard.client_base import SLClientBase
from snowleopard.models import ResponseDataObjects, RetrieveResponseObjects, parse


class AsyncSnowLeopardClient(SLClientBase):
    client: httpx.AsyncClient

    def __init__(
        self,
        loc: str = None,
        token: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
    ):
        config = self._config(loc, token, timeout)
        self.client = httpx.AsyncClient(
            base_url=config.loc,
            headers=config.headers(),
            timeout=config.timeout
        )

    async def retrieve(
        self, datafile_id: str, user_query: str
    ) -> RetrieveResponseObjects:
        resp = await self.client.post(
            url=self._build_path(datafile_id, "retrieve"),
            json={"userQuery": user_query},
        )
        return self._parse_retrieve(resp)

    async def response(self, datafile_id: str, user_query: str) -> AsyncGenerator[ResponseDataObjects, None]:
        async with self.client.stream(
            "POST",
            self._build_path(datafile_id, "response"),
            json={"userQuery": user_query},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                yield parse(json.loads(line))

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        await self.client.aclose()
