import os
from typing import Optional

import httpx
from snowleopard.errors import APIError
from snowleopard.models import RetrieveResponse, SchemaData, ResponseStatus


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

    async def retrieve(self, datafile_id: str, user_query: str) -> RetrieveResponse:
        resp = await self.client.post(
            # url=f"/datafiles/{datafile_id}/retrieve",
            url=f"api/self/datafiles/{datafile_id}/proxy/retrieve",
            json={"userQuery": user_query},
        )
        if resp.status_code >= 300 and resp.status_code != 409:
            raise APIError(resp.reason_phrase, resp)

        resp_json = resp.json()

        if "__type__" not in resp_json:
            raise APIError('Unable to parse response without "__type__" field', resp)

        response_type = resp_json["__type__"]
        if response_type == "apiError":
            raise APIError(resp_json["description"], resp)
        elif response_type == "httpError":
            raise APIError(resp_json["description"], resp)
        elif response_type == "retrieveResponse":
            # todo, we need to parse this in a less terrible way, but unsure if we want to introduce additional dependencies
            return RetrieveResponse(
                callId=resp_json["callId"],
                data=[
                    SchemaData(
                        schemaId=d["schemaId"],
                        schemaType=d["schemaType"],
                        query=d["query"],
                        rows=d["rows"],
                        querySummary=d["querySummary"],
                        rowMax=d["rowMax"],
                        isTrimmed=d["isTrimmed"],
                    )
                    for d in resp_json["data"]
                ],
                responseStatus=ResponseStatus(resp_json["responseStatus"]),
            )
        else:
            raise APIError(f'unknown response type "{response_type}"', resp)

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        await self.client.aclose()
