import os
from typing import Optional

import httpx
from snowleopard.models import RetrieveResponse, parse, RetrieveResponseError


class AsyncSnowLeopardClient:
    client: httpx.AsyncClient

    def __init__(
        self,
        loc: str = None,
        token: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
    ):
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

        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.client = httpx.AsyncClient(
            base_url=loc,
            headers=headers,
            timeout=timeout
            or httpx.Timeout(connect=5.0, read=600.0, write=10.0, pool=5.0),
        )

    async def retrieve(
        self, datafile_id: str, user_query: str
    ) -> RetrieveResponse | RetrieveResponseError:
        resp = await self.client.post(
            # url=f"/datafiles/{datafile_id}/retrieve",
            url=f"api/self/datafiles/{datafile_id}/proxy/retrieve",
            json={"userQuery": user_query},
        )
        try:
            return parse(resp.json())
        except Exception:
            resp.raise_for_status()
            raise

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        await self.client.aclose()
